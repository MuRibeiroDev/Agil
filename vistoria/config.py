# Configuração do Banco de Dados PostgreSQL
# Arquivo: config.py

import os
from pathlib import Path

# Configurações do banco de dados
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'agil'),
    'user': os.getenv('DB_USER', '123'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'minconn': int(os.getenv('DB_MIN_CONN', '2')),
    'maxconn': int(os.getenv('DB_MAX_CONN', '10'))
}

# Configurações da aplicação
APP_CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
    'DEBUG': os.getenv('FLASK_ENV', 'development') == 'development',
    'HOST': os.getenv('FLASK_HOST', '0.0.0.0'),
    'PORT': int(os.getenv('FLASK_PORT', '5000'))
}

# Configurações de upload
UPLOAD_CONFIG = {
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'UPLOAD_FOLDER': Path(__file__).parent / 'uploads'
}

# Configurações de assinatura
SIGNATURE_CONFIG = {
    'FOLDER': Path(__file__).parent / 'assinaturas',
    'MAX_SIZE': 2 * 1024 * 1024,  # 2MB
    'FORMAT': 'PNG'
}

# Criação automática de diretórios
UPLOAD_CONFIG['UPLOAD_FOLDER'].mkdir(exist_ok=True)
SIGNATURE_CONFIG['FOLDER'].mkdir(exist_ok=True)

# Configurações de token de assinatura
TOKEN_CONFIG = {
    'EXPIRATION_HOURS': int(os.getenv('TOKEN_EXPIRATION_HOURS', '72')),  # 72 horas padrão
    'LENGTH': 32
}

# Função para obter configuração do banco
def get_database_url():
    """Retorna URL de conexão do PostgreSQL"""
    config = DATABASE_CONFIG
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Função para validar configurações
def validate_config():
    """Valida se todas as configurações estão corretas"""
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"⚠️  Variáveis de ambiente ausentes: {', '.join(missing)}")
        print("💡 Usando valores padrão. Configure as variáveis para produção.")
    
    return len(missing) == 0
