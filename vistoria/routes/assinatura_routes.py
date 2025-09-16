"""
Rotas de assinatura remota
"""
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from db import get_vistoria_db
from utils import save_signature_image, save_vistoria_complete

assinatura_bp = Blueprint('assinatura', __name__)


def prepare_vistoria_data_for_saving(vistoria_data):
    """
    Converte dados básicos do frontend para o formato esperado pelo save_vistoria_complete
    
    Args:
        vistoria_data (dict): Dados da vistoria do frontend
        
    Returns:
        dict: Dados formatados para salvamento (sem fotos - devem ser adicionadas depois)
    """
    return {
        'veiculo': {
            'placa': vistoria_data.get('veiculo', {}).get('placa', ''),
            'chassi': vistoria_data.get('veiculo', {}).get('chassi', ''),  # ADICIONADO CHASSI
            'modelo': vistoria_data.get('veiculo', {}).get('modelo', ''),
            'cor': vistoria_data.get('veiculo', {}).get('cor', ''),
            'ano': vistoria_data.get('veiculo', {}).get('ano', ''),
            'km_rodado': vistoria_data.get('veiculo', {}).get('km_rodado', ''),
            'proprio': vistoria_data.get('veiculo', {}).get('proprio', True),
            'nome_terceiro': vistoria_data.get('veiculo', {}).get('nome_terceiro', ''),
            'documento_nota_fiscal': ''  # Será atualizado se houver upload
        },
        'questionario': vistoria_data.get('questionario', {}),
        'pneus': vistoria_data.get('pneus', {}),
        'nome_conferente': vistoria_data.get('nome_conferente', ''),
        'nome_cliente': vistoria_data.get('nome_cliente', ''),  # nome_cliente fica no nível raiz
        'data_vistoria': vistoria_data.get('data_vistoria', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    }


@assinatura_bp.route('/api/gerar_link_assinatura', methods=['POST'])
def gerar_link_assinatura():
    """Gerar link único para assinatura remota do cliente - salva no banco"""
    try:
        # Receber dados da vistoria
        vistoria_data = request.get_json()
        
        print(f"🔗 Gerando link para: {vistoria_data.get('placa', 'N/A')}")
        print(f"🔍 DEBUG: Dados recebidos para link: {vistoria_data}")
        print(f"🔍 DEBUG: nome_cliente recebido: '{vistoria_data.get('nome_cliente', 'AUSENTE')}'")
        print(f"🔍 DEBUG: nome_terceiro recebido: '{vistoria_data.get('veiculo', {}).get('nome_terceiro', 'AUSENTE')}'")
        
        
        # Testar conexão com o banco antes de salvar
        try:
            vistoria_db = get_vistoria_db()
            print("✅ Conexão com banco OK para gerar link")
        except Exception as db_error:
            print(f"❌ Erro de conexão com banco: {db_error}")
            return jsonify({
                'success': False,
                'message': f'Erro de conexão com banco: {str(db_error)}'
            }), 500
        
        # Usar a função auxiliar para preparar os dados
        dados_convertidos = prepare_vistoria_data_for_saving(vistoria_data)
        
        # Adicionar questionário (mantém compatibilidade)
        questionario = vistoria_data.get('questionario', {})
        for key, value in questionario.items():
            dados_convertidos[key] = value
        
        # CORREÇÃO: Adicionar campos de observação que estão no nível raiz
        for key, value in vistoria_data.items():
            if key.startswith('desc_obs_'):
                dados_convertidos[key] = value
        
        # Processar fotos do formato JSON (IGUAL À ROTA SALVAR_VISTORIA_COMPLETA)
        photos_data = []
        
        # Processar fotos do campo 'fotos' (formato antigo)
        fotos = vistoria_data.get('fotos', {})
        for field_name, foto_data in fotos.items():
            if foto_data and foto_data.get('url'):
                photos_data.append({
                    'category': field_name,
                    'name': field_name,
                    'url': foto_data['url'],
                    'size': foto_data.get('size', 0),
                    'type': foto_data.get('type', 'image/jpeg')
                })
        
        # Processar fotos do campo 'photos' (formato novo - incluindo documento)
        photos_array = vistoria_data.get('photos', [])
        for photo in photos_array:
            if photo and photo.get('url'):
                photos_data.append({
                    'category': photo['category'],
                    'name': photo['name'],
                    'url': photo['url'],
                    'size': photo.get('size', 0),
                    'type': photo.get('type', 'image/jpeg')
                })
        
        dados_convertidos['photos'] = photos_data
        
        print(f"🔍 DEBUG: Total de fotos processadas: {len(photos_data)}")
        for i, photo in enumerate(photos_data):
            print(f"🔍 DEBUG: Foto {i+1}: category={photo['category']}, name={photo['name']}, type={photo['type']}")
        
        # Processar documento se fornecido
        documento = vistoria_data.get('documento')
        if documento and documento.get('file'):
            # Documento será processado pelo vistoria_utils
            dados_convertidos['documento'] = documento
        
        print(f"🔧 Convertido {len(photos_data)} fotos para processamento")
        
        # Salvar vistoria no banco primeiro
        print("🔧 Iniciando salvamento da vistoria...")
        result = save_vistoria_complete(dados_convertidos)
        print(f"🔍 Resultado do salvamento: {result}")
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar vistoria: {result["error"]}'
            }), 500
        
        vistoria_id = result['vistoria_id']
        token = result['token']
        
        # Calcular expiração (24 horas)
        expiration = datetime.now() + timedelta(hours=24)
        
        return jsonify({
            'success': True,
            'token': token,
            'vistoria_id': vistoria_id,
            'expires_at': expiration.isoformat(),
            'message': 'Link de assinatura gerado e vistoria salva no banco'
        })
        
    except Exception as e:
        print(f"❌ Erro ao gerar link: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@assinatura_bp.route('/assinatura_cliente')
def assinatura_cliente():
    """Página de assinatura para o cliente - verifica no banco"""
    token = request.args.get('token')
    
    if not token:
        return render_template('link_expirado.html'), 404
    
    try:
        vistoria_db = get_vistoria_db()
        vistoria = vistoria_db.buscar_vistoria_por_token(token)
        
        if not vistoria:
            return render_template('link_expirado.html'), 404
        
        # Verificar se não expirou
        if vistoria['token_expira_em'] and datetime.now() > vistoria['token_expira_em']:
            return render_template('link_expirado.html'), 410  # Token expirado
        
        # Verificar se já foi assinado
        if vistoria['status'] == 'assinado':
            return render_template('link_expirado.html'), 410  # Já assinado
        
        return render_template('assinatura_cliente.html')
        
    except Exception as e:
        print(f"❌ Erro ao verificar token: {e}")
        return render_template('link_expirado.html'), 500


@assinatura_bp.route('/api/dados_vistoria_cliente')
def dados_vistoria_cliente():
    """Retornar dados da vistoria para o cliente assinar - do banco"""
    token = request.args.get('token')
    
    print(f"🔍 API chamada com token: {token}")
    
    if not token:
        return jsonify({
            'success': False,
            'message': 'Token não fornecido'
        }), 400
    
    try:
        vistoria_db = get_vistoria_db()
        vistoria = vistoria_db.buscar_vistoria_por_token(token)
        
        print(f"🔍 Vistoria encontrada: {vistoria is not None}")
        if vistoria:
            print(f"🔍 Dados da vistoria: placa={vistoria.get('placa')}, modelo={vistoria.get('modelo')}")
        
        if not vistoria:
            return jsonify({
                'success': False,
                'message': 'Token inválido ou vistoria não encontrada'
            }), 404
        
        # Verificar expiração
        if vistoria['token_expira_em'] and datetime.now() > vistoria['token_expira_em']:
            return jsonify({
                'success': False,
                'message': 'Link expirado'
            }), 410
        
        # Verificar se já foi assinado
        if vistoria['status'] == 'assinado':
            return jsonify({
                'success': False,
                'message': 'Esta vistoria já foi assinada. O link não é mais válido.'
            }), 410
        
        # Buscar fotos da vistoria
        fotos = vistoria_db.buscar_fotos_vistoria(vistoria['id'])
        print(f"🔍 Fotos encontradas: {len(fotos) if fotos else 0}")
        if fotos:
            print(f"🔍 Primeira foto: {fotos[0] if len(fotos) > 0 else 'Nenhuma'}")
        
        # CORREÇÃO TEMPORÁRIA: Se não há fotos no banco, buscar no backup JSON
        if not fotos:
            print("⚠️ Nenhuma foto encontrada no banco, tentando buscar no backup...")
            # Buscar arquivo de backup da vistoria
            import os
            import json
            backup_dir = 'vistorias_backup'
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if f.startswith(f'vistoria_{vistoria["token"]}_')]
                if backup_files:
                    latest_backup = max(backup_files)
                    backup_path = os.path.join(backup_dir, latest_backup)
                    try:
                        with open(backup_path, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                        
                        # Extrair fotos do backup
                        backup_fotos = backup_data.get('dados_originais', {}).get('fotos', {})
                        fotos = []
                        for field_name, foto_data in backup_fotos.items():
                            if foto_data and foto_data.get('url'):
                                # Determinar tipo baseado na categoria
                                if field_name == 'documento_nota_fiscal':
                                    tipo = 'documento'
                                elif 'pneu' in field_name.lower():
                                    tipo = 'pneu'
                                elif 'obs' in field_name.lower():
                                    tipo = 'observacao'
                                else:
                                    tipo = 'obrigatoria'
                                    
                                fotos.append({
                                    'categoria': field_name,
                                    'tipo': tipo,
                                    'arquivo_nome': f'{field_name}.jpg',
                                    'arquivo_path': '',
                                    'arquivo_url': foto_data['url'],
                                    'observacao_descricao': None
                                })
                        print(f"✅ {len(fotos)} fotos recuperadas do backup")
                    except Exception as e:
                        print(f"❌ Erro ao ler backup: {e}")
        
        # Converter dados do banco para formato do frontend
        vistoria_data = {
            'placa': vistoria['placa'],
            'chassi': vistoria['chassi'],  # ADICIONADO CHASSI
            'modelo': vistoria['modelo'],
            'cor': vistoria['cor'],
            'ano': vistoria['ano'],
            'km_rodado': vistoria['km_rodado'],  # ADICIONADO CAMPO KM_RODADO
            'proprio': vistoria['proprio'],  # ADICIONADO CAMPO PROPRIO
            'nome_terceiro': vistoria['nome_terceiro'],  # ADICIONADO NOME_TERCEIRO
            'nome_cliente': vistoria['nome_cliente'],  # ADICIONADO NOME_CLIENTE
            'nome_conferente': vistoria['nome_conferente'],
            'criado_em': vistoria['criado_em'].isoformat() if vistoria['criado_em'] else None,
            
            # Questionário
            'ar_condicionado': vistoria['ar_condicionado'],
            'antenas': vistoria['antenas'],
            'tapetes': vistoria['tapetes'],
            'tapete_porta_malas': vistoria['tapete_porta_malas'],
            'bateria': vistoria['bateria'],
            'retrovisor_direito': vistoria['retrovisor_direito'],
            'retrovisor_esquerdo': vistoria['retrovisor_esquerdo'],
            'extintor': vistoria['extintor'],
            'roda_comum': vistoria['roda_comum'],
            'roda_especial': vistoria['roda_especial'],
            'chave_principal': vistoria['chave_principal'],
            'chave_reserva': vistoria['chave_reserva'],
            'manual': vistoria['manual'],
            'documento': vistoria['documento'],
            'nota_fiscal': vistoria['nota_fiscal'],
            'limpador_dianteiro': vistoria['limpador_dianteiro'],
            'limpador_traseiro': vistoria['limpador_traseiro'],
            'triangulo': vistoria['triangulo'],
            'macaco': vistoria['macaco'],
            'chave_roda': vistoria['chave_roda'],
            'pneu_step': vistoria['pneu_step'],
            'carregador_eletrico': vistoria['carregador_eletrico'],  # ADICIONADO CARREGADOR ELÉTRICO
            
            # Marcas dos pneus
            'marca_pneu_de': vistoria['marca_pneu_dianteiro_esquerdo'],
            'marca_pneu_dd': vistoria['marca_pneu_dianteiro_direito'],
            'marca_pneu_te': vistoria['marca_pneu_traseiro_esquerdo'],
            'marca_pneu_td': vistoria['marca_pneu_traseiro_direito'],
            
            # Fotos
            'photos': []
        }
        
        # Adicionar fotos
        for i, foto in enumerate(fotos):
            print(f"🔍 Processando foto {i+1}: categoria={foto.get('categoria')}, url={foto.get('arquivo_url')}, path={foto.get('arquivo_path')}")
            photo_data = {
                'category': foto['categoria'],
                'name': foto['categoria'],
                'url': foto['arquivo_url'] or foto['arquivo_path'],
                'type': foto['tipo']
            }
            
            # Adicionar observação se houver
            if foto.get('observacao_descricao'):
                photo_data['observacao'] = foto['observacao_descricao']
            
            vistoria_data['photos'].append(photo_data)
        
        print(f"🔍 Total de fotos adicionadas: {len(vistoria_data['photos'])}")
        
        return jsonify({
            'success': True,
            'vistoria': vistoria_data
        })
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados da vistoria: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@assinatura_bp.route('/api/confirmar_assinatura_cliente', methods=['POST'])
def confirmar_assinatura_cliente():
    """Confirmar assinatura do cliente - salva no banco"""
    try:
        data = request.get_json()
        token = data.get('token')
        signature = data.get('signature')
        cliente_nome = data.get('cliente_nome', 'Cliente')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token não fornecido'
            }), 400
        
        if not signature:
            return jsonify({
                'success': False,
                'message': 'Assinatura é obrigatória'
            }), 400
        
        vistoria_db = get_vistoria_db()
        vistoria = vistoria_db.buscar_vistoria_por_token(token)
        
        if not vistoria:
            return jsonify({
                'success': False,
                'message': 'Token inválido'
            }), 404
        
        # Verificar expiração
        if vistoria['token_expira_em'] and datetime.now() > vistoria['token_expira_em']:
            return jsonify({
                'success': False,
                'message': 'Link expirado'
            }), 410
        
        # Verificar se já foi assinado
        if vistoria['status'] == 'assinado':
            return jsonify({
                'success': False,
                'message': 'Esta vistoria já foi assinada anteriormente'
            }), 410
        
        # Salvar assinatura como arquivo
        signature_info = save_signature_image(signature, token)
        
        if not signature_info:
            return jsonify({
                'success': False,
                'message': 'Erro ao salvar assinatura'
            }), 500
        
        # Atualizar vistoria no banco
        resultado = vistoria_db.atualizar_assinatura_vistoria(
            token=token,
            assinatura_path=signature_info['path'],
            cliente_nome=cliente_nome,
            checksum=signature_info['checksum']
        )
        
        if not resultado:
            return jsonify({
                'success': False,
                'message': 'Erro ao registrar assinatura no banco'
            }), 500
        
        print(f"✅ Assinatura confirmada: {resultado['placa']} - {resultado['modelo']}")
        
        return jsonify({
            'success': True,
            'message': 'Assinatura confirmada com sucesso',
            'veiculo': {
                'placa': resultado['placa'],
                'modelo': resultado['modelo']
            }
        })
        
    except Exception as e:
        print(f"❌ Erro ao confirmar assinatura: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
