#!/usr/bin/env python3
"""
Database Configuration and Connection - VERSÃO COM IDs SEQUENCIAIS
Sistema Vistoria Agil - PostgreSQL Integration
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import logging
from datetime import datetime
import hashlib
import secrets
import string

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configurações do banco de dados"""
    
    # Configurações padrão - AJUSTE CONFORME SEU AMBIENTE
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'agil')  # Voltando para o banco que estava funcionando
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123')  # Voltando para a senha que estava funcionando
    
    # Pool de conexões
    MIN_CONNECTIONS = 1
    MAX_CONNECTIONS = 10
    
    @classmethod
    def get_connection_string(cls):
        """Gerar string de conexão PostgreSQL"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_connection_params(cls):
        """Parâmetros de conexão como dicionário"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'cursor_factory': RealDictCursor
        }

class DatabaseManager:
    """Gerenciador de pool de conexões PostgreSQL"""
    
    def __init__(self):
        self.pool = None
        self.initialize_pool()
    
    def initialize_pool(self):
        """Inicializar pool de conexões"""
        try:
            self.pool = SimpleConnectionPool(
                DatabaseConfig.MIN_CONNECTIONS,
                DatabaseConfig.MAX_CONNECTIONS,
                **DatabaseConfig.get_connection_params()
            )
            logger.info("✅ Pool de conexões PostgreSQL inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar pool: {e}")
            raise
    
    def get_connection(self):
        """Obter conexão do pool"""
        try:
            return self.pool.getconn()
        except Exception as e:
            logger.error(f"❌ Erro ao obter conexão: {e}")
            raise
    
    def return_connection(self, conn):
        """Retornar conexão para o pool"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"❌ Erro ao retornar conexão: {e}")
    
    def close_all_connections(self):
        """Fechar todas as conexões do pool"""
        try:
            if self.pool:
                self.pool.closeall()
                logger.info("✅ Todas as conexões fechadas")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar conexões: {e}")

class VistoriaDatabase:
    """Classe principal para operações de banco da Vistoria"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def gerar_token_unico(self):
        """Gerar token único para assinatura"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Gerar ID aleatório mais curto
        chars = string.ascii_uppercase + string.digits
        random_id = ''.join(secrets.choice(chars) for _ in range(12))
        return f"VIST_{random_id}_{timestamp}"
    
    def calcular_checksum_arquivo(self, file_path):
        """Calcular hash SHA256 do arquivo"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            logger.error(f"❌ Erro ao calcular checksum: {e}")
            return None
    
    def inserir_vistoria(self, dados_vistoria):
        """Inserir nova vistoria no banco de dados"""
        conn = None
        try:
            print(f"🔧 [DB] Iniciando inserção da vistoria...")
            print(f"🔧 [DB] Dados recebidos: {list(dados_vistoria.keys())}")
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Gerar token único
            token = self.gerar_token_unico()
            print(f"🔧 [DB] Token gerado: {token}")
            
            # SQL de inserção - REMOVIDO documento_nota_fiscal
            sql = """
            INSERT INTO vistorias (
                token, placa, modelo, cor, ano, nome_conferente, nome_cliente, km_rodado,
                proprio, nome_terceiro,
                ar_condicionado, antenas, tapetes, tapete_porta_malas, bateria,
                retrovisor_direito, retrovisor_esquerdo, extintor, roda_comum, roda_especial,
                chave_principal, chave_reserva, manual, documento, nota_fiscal,
                limpador_dianteiro, limpador_traseiro, triangulo, macaco, chave_roda, pneu_step, carregador_eletrico,
                marca_pneu_dianteiro_esquerdo, marca_pneu_dianteiro_direito,
                marca_pneu_traseiro_esquerdo, marca_pneu_traseiro_direito,
                token_expira_em, status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                CURRENT_TIMESTAMP + INTERVAL '24 hours', 'aguardando_assinatura'
            ) RETURNING id, token
            """
            
            # Preparar dados
            # Suporte para dados estruturados (objeto) e dados planos (form-data)
            if 'veiculo' in dados_vistoria:
                # Formato estruturado (objeto JSON)
                veiculo = dados_vistoria.get('veiculo', {})
                questionario = dados_vistoria.get('questionario', {})
                pneus = dados_vistoria.get('pneus', {})
            else:
                # Formato plano (form-data) - reestruturar dados
                proprio_raw = dados_vistoria.get('proprio', 'true')
                nome_terceiro_raw = dados_vistoria.get('nome_terceiro', '')
                
                proprio_convertido = proprio_raw.lower() == 'true' if isinstance(proprio_raw, str) else bool(proprio_raw)
                
                veiculo = {
                    'placa': dados_vistoria.get('placa', ''),
                    'modelo': dados_vistoria.get('modelo', ''),
                    'cor': dados_vistoria.get('cor', ''),
                    'ano': dados_vistoria.get('ano', ''),
                    'km_rodado': dados_vistoria.get('km_rodado', ''),
                    'proprio': proprio_convertido,  # Usar valor convertido
                    'nome_terceiro': nome_terceiro_raw
                }
                
                # Mapear questionário
                questionario = {}
                questionario_fields = [
                    'ar_condicionado', 'antenas', 'tapetes', 'tapete_porta_malas', 'bateria',
                    'retrovisor_direito', 'retrovisor_esquerdo', 'extintor', 'roda_comum', 'roda_especial',
                    'chave_principal', 'chave_reserva', 'manual', 'documento', 'nota_fiscal',
                    'limpador_dianteiro', 'limpador_traseiro', 'triangulo', 'macaco', 'chave_roda', 'pneu_step', 'carregador_eletrico'
                ]
                
                for field in questionario_fields:
                    questionario[field] = dados_vistoria.get(field, 'false').lower() == 'true'
                
                # Mapear pneus
                pneus = {
                    'marca_pneu_dianteiro_esquerdo': dados_vistoria.get('marca_pneu_dianteiro_esquerdo', ''),
                    'marca_pneu_dianteiro_direito': dados_vistoria.get('marca_pneu_dianteiro_direito', ''),
                    'marca_pneu_traseiro_esquerdo': dados_vistoria.get('marca_pneu_traseiro_esquerdo', ''),
                    'marca_pneu_traseiro_direito': dados_vistoria.get('marca_pneu_traseiro_direito', '')
                }
            
            # DEBUG: Log dos dados dos pneus
            print(f"🔍 [DEBUG] Dados completos dos pneus recebidos: {pneus}")
            print(f"🔍 [DEBUG] Marca pneu DE: '{pneus.get('marca_pneu_dianteiro_esquerdo', '')}'")
            print(f"🔍 [DEBUG] Marca pneu DD: '{pneus.get('marca_pneu_dianteiro_direito', '')}'")
            print(f"🔍 [DEBUG] Marca pneu TE: '{pneus.get('marca_pneu_traseiro_esquerdo', '')}'")
            print(f"🔍 [DEBUG] Marca pneu TD: '{pneus.get('marca_pneu_traseiro_direito', '')}'")
            
            # Validar e processar o ano
            ano_raw = veiculo.get('ano')
            ano_valido = None
            if ano_raw:
                try:
                    ano_int = int(ano_raw)
                    # Validar se o ano está dentro de um range válido (1900 até ano atual + 1)
                    ano_atual = datetime.now().year
                    if 1900 <= ano_int <= ano_atual + 1:
                        ano_valido = ano_int
                    else:
                        print(f"⚠️ Ano inválido ({ano_int}), usando None")
                except (ValueError, TypeError):
                    print(f"⚠️ Ano não numérico ({ano_raw}), usando None")
            
            # Preparar valores finais
            proprio_final = veiculo.get('proprio', True)  # Boolean, padrão True (próprio)
            nome_terceiro_final = veiculo.get('nome_terceiro', '') or None  # Nome do terceiro se não for próprio
            
            valores = (
                token,
                veiculo.get('placa', '') or None,  # Permite null se vazio
                veiculo.get('modelo', ''),  # Obrigatório
                veiculo.get('cor', ''),  # Obrigatório
                ano_valido,  # Pode ser None
                dados_vistoria.get('nome_conferente', ''),  # Obrigatório
                dados_vistoria.get('nome_cliente', ''),  # Obrigatório
                veiculo.get('km_rodado', '') or None,  # Campo KM, permite null se vazio
                
                # Campos de propriedade do veículo
                proprio_final,
                nome_terceiro_final,
                
                # Questionário
                questionario.get('ar_condicionado', False),
                questionario.get('antenas', False),
                questionario.get('tapetes', False),
                questionario.get('tapete_porta_malas', False),
                questionario.get('bateria', False),
                questionario.get('retrovisor_direito', False),
                questionario.get('retrovisor_esquerdo', False),
                questionario.get('extintor', False),
                questionario.get('roda_comum', False),
                questionario.get('roda_especial', False),
                questionario.get('chave_principal', False),
                questionario.get('chave_reserva', False),
                questionario.get('manual', False),
                questionario.get('documento', False),
                questionario.get('nota_fiscal', False),
                questionario.get('limpador_dianteiro', False),
                questionario.get('limpador_traseiro', False),
                questionario.get('triangulo', False),
                questionario.get('macaco', False),
                questionario.get('chave_roda', False),
                questionario.get('pneu_step', False),
                questionario.get('carregador_eletrico', False),
                
                # Marcas dos pneus
                pneus.get('marca_pneu_dianteiro_esquerdo', ''),
                pneus.get('marca_pneu_dianteiro_direito', ''),
                pneus.get('marca_pneu_traseiro_esquerdo', ''),
                pneus.get('marca_pneu_traseiro_direito', '')
            )
            
            print(f"🔧 [DB] Executando SQL...")
            print(f"🔍 [DEBUG] SQL count de %s: {sql.count('%s')}")
            print(f"🔍 [DEBUG] Número de valores fornecidos: {len(valores)}")
            print(f"🔍 [DEBUG] Valores: {valores}")
            
            cursor.execute(sql, valores)
            resultado = cursor.fetchone()
            vistoria_id = resultado['id']
            token_retornado = resultado['token']
            
            print(f"✅ [DB] Vistoria inserida com ID sequencial: {vistoria_id}")
            print(f"✅ [DB] Token: {token_retornado}")
            
            # Commit para finalizar inserção da vistoria
            conn.commit()
            
            return {
                'id': vistoria_id,
                'token': token_retornado,
                'success': True
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Erro ao inserir vistoria: {e}")
            raise
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def inserir_foto_vistoria(self, vistoria_id, categoria, arquivo_info):
        """Inserir foto da vistoria"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Determinar tipo da foto
            if 'pneu' in categoria.lower():
                tipo = 'pneu'
            elif 'obs' in categoria.lower() or 'observacao' in categoria.lower():
                tipo = 'observacao'
            elif categoria == 'documento_nota_fiscal':
                tipo = 'documento'
            else:
                tipo = 'obrigatoria'
            
            sql = """
            INSERT INTO fotos_vistoria (
                vistoria_id, categoria, tipo, arquivo_nome, arquivo_path,
                arquivo_url, arquivo_tamanho, arquivo_tipo, arquivo_checksum
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
            """
            
            valores = (
                vistoria_id,
                categoria,
                tipo,
                arquivo_info.get('filename', ''),
                arquivo_info.get('path', ''),
                arquivo_info.get('url', ''),
                arquivo_info.get('size', 0),
                arquivo_info.get('mimetype', 'image/jpeg'),
                arquivo_info.get('checksum', '')
            )
            
            cursor.execute(sql, valores)
            foto_id = cursor.fetchone()['id']
            
            conn.commit()
            
            print(f"✅ [DB] Foto inserida com ID sequencial: {foto_id}")
            
            return foto_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Erro ao inserir foto: {e}")
            raise
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def inserir_observacao_foto(self, foto_vistoria_id, descricao, tipo='dano', gravidade='baixa', prioridade='normal'):
        """Inserir observação de uma foto"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO observacoes_fotos_vistoria (
                foto_vistoria_id, descricao, tipo, gravidade, prioridade
            ) VALUES (
                %s, %s, %s, %s, %s
            ) RETURNING id
            """
            
            cursor.execute(sql, (foto_vistoria_id, descricao, tipo, gravidade, prioridade))
            observacao_id = cursor.fetchone()['id']
            
            conn.commit()
            
            print(f"✅ [DB] Observação inserida com ID sequencial: {observacao_id}")
            
            return observacao_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Erro ao inserir observação: {e}")
            raise
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def buscar_fotos_vistoria(self, vistoria_id):
        """Buscar fotos de uma vistoria com observações"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                f.id as foto_id,
                f.categoria,
                f.tipo,
                f.arquivo_nome,
                f.arquivo_path,
                f.arquivo_url,
                f.criado_em as foto_criado_em,
                o.id as observacao_id,
                o.descricao as observacao_descricao,
                o.prioridade as observacao_prioridade,
                o.status as observacao_status
            FROM fotos_vistoria f
            LEFT JOIN observacoes_fotos_vistoria o ON f.id = o.foto_vistoria_id AND o.status = 'ativa'
            WHERE f.vistoria_id = %s
            ORDER BY 
                CASE f.tipo 
                    WHEN 'obrigatoria' THEN 1 
                    WHEN 'pneu' THEN 2 
                    WHEN 'observacao' THEN 3 
                END,
                f.categoria, f.id
            """
            
            cursor.execute(sql, (vistoria_id,))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fotos: {e}")
            raise
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def buscar_vistoria_por_token(self, token):
        """Buscar vistoria pelo token"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT * FROM vistorias WHERE token = %s
            """
            
            cursor.execute(sql, (token,))
            result = cursor.fetchone()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar vistoria por token: {e}")
            return None
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def buscar_vistoria_por_id(self, vistoria_id):
        """Buscar vistoria por ID sequencial"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT * FROM vistorias WHERE id = %s
            """
            
            cursor.execute(sql, (vistoria_id,))
            result = cursor.fetchone()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar vistoria por ID: {e}")
            return None
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def atualizar_assinatura_vistoria(self, token, assinatura_path, cliente_nome, checksum=None):
        """Atualizar vistoria com dados da assinatura"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            UPDATE vistorias SET
                assinatura_arquivo_path = %s,
                assinatura_cliente_nome = %s,
                assinatura_data = CURRENT_TIMESTAMP,
                assinatura_checksum = %s,
                status = 'assinado',
                atualizado_em = CURRENT_TIMESTAMP
            WHERE token = %s AND status = 'aguardando_assinatura'
            RETURNING id, placa, modelo, token
            """
            
            cursor.execute(sql, (assinatura_path, cliente_nome, checksum, token))
            resultado = cursor.fetchone()
            
            if resultado:
                conn.commit()
                vistoria_id = resultado['id']
                print(f"✅ [DB] Assinatura salva para vistoria ID: {vistoria_id}")
                return {
                    'id': resultado['id'],
                    'placa': resultado['placa'],
                    'modelo': resultado['modelo'],
                    'token': resultado['token']
                }
            else:
                conn.rollback()
                print(f"❌ [DB] Token inválido ou vistoria já assinada: {token}")
                return None
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Erro ao atualizar assinatura: {e}")
            raise
        finally:
            if conn:
                self.db_manager.return_connection(conn)
    
    def listar_vistorias_recentes(self, limite=10):
        """Listar vistorias mais recentes"""
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            SELECT 
                id,
                token,
                placa,
                modelo,
                cor,
                ano,
                nome_conferente,
                status,
                criado_em,
                assinatura_data,
                assinatura_cliente_nome
            FROM vistorias 
            ORDER BY criado_em DESC
            LIMIT %s
            """
            
            cursor.execute(sql, (limite,))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar vistorias: {e}")
            return []
        finally:
            if conn:
                self.db_manager.return_connection(conn)

# Instância global da classe
_database_manager = None
_vistoria_db = None

def init_database():
    """Inicializar o banco de dados"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def get_vistoria_db():
    """Obter instância global do banco de vistorias"""
    global _vistoria_db
    if _vistoria_db is None:
        _vistoria_db = VistoriaDatabase()
    return _vistoria_db

def close_database():
    """Fechar todas as conexões do banco"""
    global _database_manager
    if _database_manager:
        _database_manager.close_all_connections()
        _database_manager = None

def test_connection():
    """Testar conexão com o banco"""
    try:
        db = get_vistoria_db()
        vistorias = db.listar_vistorias_recentes(1)
        print(f"✅ Conexão OK! Encontradas {len(vistorias)} vistorias")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    # Teste da conexão
    print("🧪 Testando conexão com o banco...")
    test_connection()
