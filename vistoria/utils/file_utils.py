"""
Utilitários para manipulação de arquivos
"""
import os
import base64
import hashlib
from datetime import datetime
from PIL import Image


def calculate_file_checksum(file_path: str) -> str:
    """
    Calcular checksum SHA256 de um arquivo
    
    Args:
        file_path (str): Caminho para o arquivo
        
    Returns:
        str: Checksum SHA256 ou None se erro
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"❌ Erro ao calcular checksum: {e}")
        return None


def save_signature_image(signature_data: str, token: str) -> dict:
    """
    Salvar assinatura digital como arquivo de imagem
    
    Args:
        signature_data (str): Data URL da assinatura (base64)
        token (str): Token único da vistoria
    
    Returns:
        dict: Informações do arquivo salvo
    """
    try:
        # Criar diretório de assinaturas se não existir
        signatures_dir = 'assinaturas'
        if not os.path.exists(signatures_dir):
            os.makedirs(signatures_dir)
        
        # Extrair dados base64 da data URL
        header, data = signature_data.split(',', 1)
        
        # Decodificar base64
        image_data = base64.b64decode(data)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'assinatura_{token}_{timestamp}.png'
        file_path = os.path.join(signatures_dir, filename)
        
        # Salvar arquivo
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Calcular checksum
        checksum = calculate_file_checksum(file_path)
        
        # Obter informações do arquivo
        file_size = os.path.getsize(file_path)
        
        print(f"✅ Assinatura salva: {file_path}")
        
        return {
            'path': file_path,
            'filename': filename,
            'size': file_size,
            'checksum': checksum,
            'mime_type': 'image/png'
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar assinatura: {e}")
        return None


def save_uploaded_photo(file, category: str, vistoria_token: str) -> dict:
    """
    Salvar foto enviada do formulário
    
    Args:
        file: Arquivo de upload do Flask
        category (str): Categoria da foto
        vistoria_token (str): Token da vistoria
        
    Returns:
        dict: Informações do arquivo salvo
    """
    try:
        # Criar diretório de uploads se não existir
        uploads_dir = 'uploads/fotos'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f'{category}_{vistoria_token}_{timestamp}.{extension}'
        file_path = os.path.join(uploads_dir, filename)
        
        # Salvar arquivo
        file.save(file_path)
        
        # Obter informações da imagem
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except:
            width, height = None, None
        
        # Calcular checksum
        checksum = calculate_file_checksum(file_path)
        
        # Obter informações do arquivo
        file_size = os.path.getsize(file_path)
        
        print(f"✅ Foto salva: {file_path}")
        
        return {
            'path': file_path,
            'filename': filename,
            'nome': file.filename,
            'size': file_size,
            'checksum': checksum,
            'mime_type': file.content_type,
            'largura': width,
            'altura': height,
            'url': f'/uploads/fotos/{filename}'
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar foto: {e}")
        return None
