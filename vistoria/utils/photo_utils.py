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
    print(f"🔍 [PHOTO_UTILS] Iniciando process_vistoria_photos com {len(photos_data)} fotos")
    foto_ids = []
    vistoria_db = get_vistoria_db()
    
    try:
        print(f"🔍 DEBUG: Processando {len(photos_data)} fotos")
        for i, photo in enumerate(photos_data):
            print(f"🔍 DEBUG: Foto {i+1}: {photo}")
            category = photo.get('category') or photo.get('name', 'unknown')
            
            # Determinar tipo da foto
            if any(x in category.lower() for x in ['pneu_', 'marca_pneu']):
                tipo = 'pneu'
            elif any(x in category.lower() for x in ['obs_', 'observacao']):
                tipo = 'observacao'
            elif category == 'documento_nota_fiscal':
                tipo = 'documento'
            else:
                tipo = 'obrigatoria'
            
            # Salvar arquivo físico
            if photo.get('url') and photo['url'].startswith('data:'):
                # Foto em base64 - salvar como arquivo
                try:
                    # Criar diretório se não existir
                    uploads_dir = 'uploads/fotos'
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                    
                    # Extrair dados base64
                    header, data = photo['url'].split(',', 1)
                    image_data = base64.b64decode(data)
                    
                    # Gerar nome do arquivo
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'{category}_{vistoria_token}_{timestamp}.jpg'
                    file_path = os.path.join(uploads_dir, filename)
                    
                    # Salvar arquivo
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Obter informações
                    file_size = os.path.getsize(file_path)
                    checksum = calculate_file_checksum(file_path)
                    
                    # Obter dimensões
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                    except:
                        width, height = None, None
                    
                    arquivo_info = {
                        'filename': filename,
                        'path': file_path,
                        'url': f'/uploads/fotos/{filename}',
                        'size': file_size,
                        'mimetype': 'image/jpeg',
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
            foto_id = vistoria_db.inserir_foto_vistoria(
                vistoria_id=vistoria_id,
                categoria=category,
                arquivo_info=arquivo_info
            )
            
            foto_ids.append(foto_id)
            print(f"✅ Foto inserida no banco: {category} - ID: {foto_id}")
        
        return foto_ids
        
    except Exception as e:
        print(f"❌ Erro ao processar fotos: {e}")
        return foto_ids
