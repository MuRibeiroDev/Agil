"""
Utilitários para processamento de fotos
"""
import os
import base64
from datetime import datetime
from PIL import Image
from db import get_vistoria_db
from .file_utils import calculate_file_checksum


def process_vistoria_photos(photos_data: list, vistoria_id: str, vistoria_token: str) -> list:
    """
    Processar e salvar fotos da vistoria no banco
    
    Args:
        photos_data (list): Lista de fotos com dados base64
        vistoria_id (str): ID da vistoria no banco
        vistoria_token (str): Token da vistoria
        
    Returns:
        list: Lista de IDs das fotos inseridas
    """
    print(f"🔍 [PHOTO_UTILS] ========== INÍCIO PROCESSAMENTO ==========")
    print(f"🔍 [PHOTO_UTILS] Vistoria ID: {vistoria_id}, Token: {vistoria_token}")
    print(f"🔍 [PHOTO_UTILS] Iniciando process_vistoria_photos com {len(photos_data)} fotos")
    
    # CORREÇÃO: Remover duplicatas baseadas na categoria
    seen_categories = set()
    unique_photos = []
    
    for i, photo in enumerate(photos_data):
        category = photo.get('category') or photo.get('name', 'unknown')
        print(f"🔍 [DEDUP] Verificando foto {i+1}: categoria='{category}', type='{photo.get('type')}'")
        
        if category not in seen_categories:
            seen_categories.add(category)
            unique_photos.append(photo)
            print(f"✅ [DEDUP] Foto aceita: {category}")
        else:
            print(f"❌ [DEDUP] Foto duplicada ignorada: {category} (type={photo.get('type')})")
    
    print(f"🔍 [DEDUP] Resultado: {len(photos_data)} -> {len(unique_photos)} fotos (removidas {len(photos_data) - len(unique_photos)} duplicatas)")
    
    foto_ids = []
    vistoria_db = get_vistoria_db()
    
    try:
        print(f"🔍 DEBUG: Processando {len(unique_photos)} fotos únicas")
        for i, photo in enumerate(unique_photos):
            print(f"🔍 DEBUG: ========== FOTO {i+1}/{len(unique_photos)} ==========")
            print(f"🔍 DEBUG: Dados completos da foto: {photo}")
            print(f"🔍 DEBUG: Foto {i+1}: categoria='{photo.get('category')}', name='{photo.get('name')}', type='{photo.get('type')}'")
            category = photo.get('category') or photo.get('name', 'unknown')
            
            # Determinar tipo da foto
            if any(x in category.lower() for x in ['pneu_', 'marca_pneu']):
                tipo = 'pneu'
            elif any(x in category.lower() for x in ['obs_', 'observacao']):
                tipo = 'observacao'
            elif category == 'documento_nota_fiscal':
                tipo = 'documento'
                print(f"📄 DEBUG: Documento detectado! Categoria: {category}")
            else:
                tipo = 'obrigatoria'
            
            print(f"🏷️ DEBUG: Tipo determinado: {tipo} para categoria: {category}")
            
                        # Salvar arquivo físico
            if photo.get('url') and photo['url'].startswith('data:'):
                # Foto em base64 - salvar como arquivo
                try:
                    # Determinar diretório baseado no tipo (usando mesmo método que vistoria_utils)
                    if tipo == 'documento':
                        uploads_dir = os.path.join('uploads', 'documentos')
                        print(f"📁 DEBUG: Salvando documento em: {uploads_dir}")
                    else:
                        uploads_dir = os.path.join('uploads', 'fotos')
                    
                    # Garantir que o diretório seja absoluto baseado no diretório atual
                    uploads_dir = os.path.abspath(uploads_dir)
                    print(f"📁 DEBUG: Diretório absoluto: {uploads_dir}")
                    print(f"📁 DEBUG: Diretório de trabalho atual: {os.getcwd()}")
                    
                    # Criar diretório se não existir
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                        print(f"📁 DEBUG: Diretório criado: {uploads_dir}")
                    else:
                        print(f"📁 DEBUG: Diretório já existe: {uploads_dir}")
                    
                    # Extrair dados base64
                    header, data = photo['url'].split(',', 1)
                    file_data = base64.b64decode(data)
                    
                    # Determinar extensão baseada no tipo MIME
                    mime_type = photo.get('type', 'image/jpeg')
                    if 'pdf' in mime_type:
                        extension = '.pdf'
                    elif 'word' in mime_type or 'msword' in mime_type:
                        extension = '.docx' if 'openxml' in mime_type else '.doc'
                    elif 'image' in mime_type:
                        if 'png' in mime_type:
                            extension = '.png'
                        elif 'gif' in mime_type:
                            extension = '.gif'
                        else:
                            extension = '.jpg'
                    else:
                        extension = '.jpg'  # fallback
                    
                    # Gerar nome do arquivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    if tipo == 'documento':
                        filename = f'documento_{vistoria_token}_{timestamp}{extension}'
                    else:
                        filename = f'{category}_{vistoria_token}_{timestamp}{extension}'
                    file_path = os.path.join(uploads_dir, filename)
                    
                    # Salvar arquivo
                    print(f"📄 DEBUG: Tentando salvar arquivo em: {file_path}")
                    print(f"📄 DEBUG: Tamanho dos dados: {len(file_data)} bytes")
                    try:
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        print(f"📄 DEBUG: Arquivo escrito com sucesso!")
                    except Exception as write_error:
                        print(f"❌ ERRO ao escrever arquivo: {write_error}")
                        raise
                    
                    if tipo == 'documento':
                        print(f"📄 DEBUG: Documento salvo com sucesso em: {file_path}")
                        print(f"📄 DEBUG: Tamanho do arquivo: {len(file_data)} bytes")
                    
                    # Verificar se o arquivo foi realmente criado
                    if os.path.exists(file_path):
                        print(f"✅ Arquivo confirmado no sistema: {file_path}")
                    else:
                        print(f"❌ ERRO: Arquivo não foi criado no sistema: {file_path}")
                    
                    # Obter informações
                    try:
                        file_size = os.path.getsize(file_path)
                        print(f"📄 DEBUG: Tamanho do arquivo confirmado: {file_size} bytes")
                    except Exception as size_error:
                        print(f"❌ ERRO ao obter tamanho do arquivo: {size_error}")
                        raise
                    
                    try:
                        checksum = calculate_file_checksum(file_path)
                        print(f"📄 DEBUG: Checksum calculado: {checksum}")
                    except Exception as checksum_error:
                        print(f"❌ ERRO ao calcular checksum: {checksum_error}")
                        raise
                    
                    # Obter dimensões (só para imagens)
                    width, height = None, None
                    if 'image' in mime_type:
                        try:
                            with Image.open(file_path) as img:
                                width, height = img.size
                        except Exception as e:
                            print(f"⚠️ Não foi possível obter dimensões da imagem {filename}: {e}")
                            width, height = None, None
                    
                    # Determinar URL baseada no tipo
                    if tipo == 'documento':
                        url_path = f'/uploads/documentos/{filename}'
                    else:
                        url_path = f'/uploads/fotos/{filename}'
                    
                    arquivo_info = {
                        'filename': filename,
                        'path': file_path,
                        'url': url_path,
                        'size': file_size,
                        'mimetype': mime_type,  # Usar o tipo MIME correto
                        'checksum': checksum,
                        'largura': width,
                        'altura': height
                    }
                    
                except Exception as e:
                    print(f"❌ Erro ao processar foto {category}: {e}")
                    continue
            else:
                # Foto já salva - usar informações existentes
                arquivo_info = {
                    'filename': photo.get('name', ''),
                    'path': '',  # Não temos o path físico
                    'url': photo.get('url', ''),
                    'size': photo.get('size'),
                    'mimetype': photo.get('type', 'image/jpeg'),
                    'checksum': '',
                    'largura': None,
                    'altura': None
                }
            
            # Inserir foto no banco
            print(f"🔍 [PHOTO_UTILS] ========== INSERINDO NO BANCO ==========")
            print(f"🔍 [PHOTO_UTILS] Categoria: {category}")
            print(f"🔍 [PHOTO_UTILS] Arquivo info: {arquivo_info}")
            
            foto_id = vistoria_db.inserir_foto_vistoria(
                vistoria_id=vistoria_id,
                categoria=category,
                arquivo_info=arquivo_info
            )
            
            foto_ids.append(foto_id)
            print(f"✅ [PHOTO_UTILS] Foto inserida no banco: {category} - ID: {foto_id}")
        
        print(f"🔍 [PHOTO_UTILS] ========== FIM PROCESSAMENTO ==========")
        print(f"🔍 [PHOTO_UTILS] Total de fotos processadas: {len(foto_ids)}")
        print(f"🔍 [PHOTO_UTILS] IDs das fotos: {foto_ids}")
        return foto_ids
        
    except Exception as e:
        print(f"❌ Erro ao processar fotos: {e}")
        return foto_ids
