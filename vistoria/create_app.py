#!/usr/bin/env python3
"""
Sistema Ágil - Vistoria de Veículos
Flask Application com PostgreSQL Integration
"""
import sys
import webbrowser
import threading
import time
from flask import Flask, request
from flask_cors import CORS

# Importar módulos organizados
from db import init_database, close_database
from routes.vistoria_routes import vistoria_bp
from routes.assinatura_routes import assinatura_bp
from routes.api_routes import api_bp


def create_app():
    """Criar e configurar a aplicação Flask"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='.',
                static_url_path='')
    
    # Configurar CORS
    CORS(app)
    
    # Configurações para otimização mobile
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache por 1 ano
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo (reduzido para mobile)
    app.config['SECRET_KEY'] = 'sistema-agil-vistoria-2025'
    
    # Headers de otimização para mobile
    @app.after_request
    def add_mobile_headers(response):
        # Cache para recursos estáticos
        if request.endpoint and 'static' in request.endpoint:
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
        
        # Headers de segurança e performance
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Compressão automática pelo navegador
        if 'gzip' in request.headers.get('Accept-Encoding', ''):
            response.headers['Vary'] = 'Accept-Encoding'
            
        return response
    
    # Inicializar banco de dados
    if not init_database():
        print("❌ Erro crítico: Não foi possível conectar ao banco de dados")
        print("🔧 Verifique as configurações em db/database.py")
        sys.exit(1)
    
    # Registrar blueprints
    app.register_blueprint(vistoria_bp)
    app.register_blueprint(assinatura_bp)
    app.register_blueprint(api_bp)
    
    return app


def open_browser():
    """Abrir navegador após o servidor estar pronto"""
    time.sleep(1.5)  # Aguardar servidor iniciar
    try:
        webbrowser.open('http://localhost:5000')
    except Exception:
        pass


def main():
    """Função principal para iniciar o servidor"""
    app = create_app()
    
    print("🚀 Sistema Ágil - Vistoria de Veículos")
    print("📍 Servidor Flask iniciado em: http://localhost:5000")
    print("🌐 Acesse: http://localhost:5000")
    print("⏹️  Pressione Ctrl+C para parar")
    print()
    
    # Abrir navegador em thread separada
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Evitar restart duplo
        )
    except KeyboardInterrupt:
        print("\n⏹️  Servidor parado pelo usuário")
        close_database()
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        close_database()
        sys.exit(1)


if __name__ == "__main__":
    main()
