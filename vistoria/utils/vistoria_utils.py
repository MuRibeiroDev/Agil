"""
Utilitários para processamento de vistoria
"""
import os
import json
import base64
from datetime import datetime
from db import get_vistoria_db
from .photo_utils import process_vistoria_photos


def save_document(document_data: dict, token: str) -> str:
    """
    Salvar documento enviado na vistoria
    
    Args:
        document_data (dict): Dados do documento com file, name, size, type
        token (str): Token da vistoria
    
    Returns:
        str: Caminho relativo do arquivo salvo
    """
    try:
        if not document_data or 'file' not in document_data:
            return ''
        
        # Criar diretório de documentos se não existir
        docs_dir = os.path.join('uploads', 'documentos')
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            print(f"📁 Pasta criada: {docs_dir}")
        
        # Gerar nome único do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = document_data.get('name', 'documento')
        file_extension = os.path.splitext(original_name)[1]
        filename = f'documento_{token}_{timestamp}{file_extension}'
        
        # Caminho completo do arquivo
        file_path = os.path.join(docs_dir, filename)
        
        # Salvar arquivo (assumindo que file é base64)
        file_content = document_data['file']
        if isinstance(file_content, str) and file_content.startswith('data:'):
            # Remover o prefixo data:mime;base64,
            base64_data = file_content.split(',')[1]
            file_bytes = base64.b64decode(base64_data)
        else:
            # Se já for bytes ou outro formato
            file_bytes = file_content
        
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        print(f"📄 Documento salvo: {file_path}")
        return f'uploads/documentos/{filename}'
        
    except Exception as e:
        print(f"❌ Erro ao salvar documento: {e}")
        return ''


def save_vistoria_complete(vistoria_data):
    """
    Salva uma vistoria completa com todas as dependências
    """
    try:
        print("🔧 [VISTORIA_UTILS] Iniciando save_vistoria_complete")
        print(f"🔍 DEBUG: Dados recebidos: {vistoria_data.keys()}")
        
        # DEBUG: Verificar especificamente os dados dos pneus
        pneus_data = vistoria_data.get('pneus', {})
        print(f"🔍 [VISTORIA_UTILS] Dados dos pneus recebidos: {pneus_data}")
        print(f"🔍 [VISTORIA_UTILS] Chaves dos pneus: {list(pneus_data.keys())}")
        
        # 1. Inserir vistoria principal
        try:
            print(f"🔧 Tentando inserir vistoria com dados: {vistoria_data.keys()}")
            vistoria_db = get_vistoria_db()
            result = vistoria_db.inserir_vistoria(vistoria_data)
            
            if not result or not isinstance(result, dict):
                raise Exception(f"Resultado inválido da inserção: {result}")
                
            vistoria_id = result['id']
            vistoria_token = result['token']
            
            print(f"✅ Vistoria inserida: ID={vistoria_id}, Token={vistoria_token}")
            
        except Exception as insert_error:
            print(f"❌ Erro específico na inserção: {insert_error}")
            raise Exception(f"Falha ao inserir vistoria: {insert_error}")
        
        # 2. Processar e salvar fotos
        photos = vistoria_data.get('photos', [])
        print(f"🔍 DEBUG: Fotos recebidas: {len(photos)}")
        
        # DEBUG: Verificar se documento está no array de fotos
        documento_encontrado = False
        for i, photo in enumerate(photos):
            category = photo.get('category')
            name = photo.get('name')
            photo_type = photo.get('type')
            print(f"🔍 DEBUG: Foto {i+1}: category='{category}', name='{name}', type='{photo_type}'")
            print(f"🔍 DEBUG: Chaves da foto: {list(photo.keys())}")
            
            if category == 'documento_nota_fiscal':
                documento_encontrado = True
                print(f"📄 Documento encontrado no array de fotos: {name}")
        
        if not documento_encontrado:
            print("⚠️ ATENÇÃO: Documento não encontrado no array de fotos!")
            print(f"🔍 DEBUG: Total de fotos recebidas: {len(photos)}")
            print(f"🔍 DEBUG: Tipos de category encontrados: {[photo.get('category') for photo in photos]}")
        
        if photos:
            foto_ids = process_vistoria_photos(photos, vistoria_id, vistoria_token)
            print(f"✅ {len(foto_ids)} fotos processadas")
        else:
            print("⚠️ Nenhuma foto encontrada para processar")
        
        # 3. Processar observações das fotos (se houver)
        observacoes_salvas = 0
        
        for i in range(1, 5):  # obs_1 até obs_4
            desc_key = f'desc_obs_{i}'
            
            if desc_key in vistoria_data and vistoria_data[desc_key].strip():
                print(f"� Processando observação {i}: {vistoria_data[desc_key]}")
                
                # Procurar foto correspondente da observação
                foto_categoria = f'foto_obs_{i}'
                
                # Encontrar a foto com essa categoria entre as fotos processadas
                foto_encontrada = False
                for j, photo in enumerate(photos):
                    if photo.get('category') == foto_categoria or photo.get('name') == foto_categoria:
                        # Aqui temos o índice da foto, foto_ids[j] seria o ID
                        if j < len(foto_ids) and foto_ids[j]:
                            foto_id = foto_ids[j]
                            descricao = vistoria_data[desc_key].strip()
                            
                            # Salvar observação no banco
                            try:
                                obs_id = vistoria_db.inserir_observacao_foto(
                                    foto_vistoria_id=foto_id,
                                    descricao=descricao,
                                    tipo='dano',
                                    gravidade='media',
                                    prioridade='normal'
                                )
                                observacoes_salvas += 1
                                print(f"✅ Observação {i} salva: ID={obs_id}, Foto={foto_id}")
                                foto_encontrada = True
                            except Exception as e:
                                print(f"❌ Erro ao salvar observação {i}: {e}")
                        break
                
                if not foto_encontrada:
                    print(f"⚠️ Foto para observação {i} não encontrada - categoria: {foto_categoria}")
            else:
                print(f"⚠️ Observação {i} vazia ou não encontrada")
        
        if observacoes_salvas > 0:
            print(f"✅ {observacoes_salvas} observações salvas no banco")
        
        # 4. Salvar backup em JSON (para segurança)
        backup_dir = 'vistorias_backup'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'vistoria_{vistoria_token}_{timestamp}.json')
        
        backup_data = {
            'vistoria_id': str(vistoria_id),
            'token': vistoria_token,
            'dados_originais': vistoria_data,
            'created_at': datetime.now().isoformat(),
            'backup_version': '1.0'
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"📋 Backup salvo: {backup_file}")
        
        return {
            'success': True,
            'vistoria_id': str(vistoria_id),
            'token': vistoria_token,
            'backup_file': backup_file
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar vistoria completa: {e}")
        return {
            'success': False,
            'error': str(e)
        }
