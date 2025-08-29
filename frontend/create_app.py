#!/usr/bin/env python3
"""
Sistema Ágil - Vistoria de Veículos
Flask Application para servir frontend e API
"""
import os
import sys
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import webbrowser
import threading
import time

def create_app():
    """Criar e configurar a aplicação Flask"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='.',
                static_url_path='')
    
    # Configurar CORS
    CORS(app)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sistema-agil-vistoria-2025'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB para uploads de fotos
    
    @app.route('/')
    def index():
        """Página principal da vistoria"""
        return render_template('index.html')
    
    @app.route('/frontend/<path:filename>')
    def frontend_static(filename):
        """Servir arquivos estáticos com prefixo /frontend/"""
        return send_from_directory('.', filename)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        """Servir arquivos de upload"""
        return send_from_directory('frontend/uploads', filename)
    
    @app.route('/api/vistoria', methods=['POST'])
    def salvar_vistoria():
        """API para salvar dados da vistoria"""
        try:
            # Processar dados do formulário
            dados = request.form.to_dict()
            arquivos = request.files
            
            # Aqui você pode implementar a lógica para salvar no banco de dados
            # Por enquanto, vamos apenas retornar sucesso
            
            return jsonify({
                'success': True,
                'message': 'Vistoria salva com sucesso!',
                'id': 'VIST-' + str(int(time.time()))
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar vistoria: {str(e)}'
            }), 500
    
    @app.route('/api/health')
    def health_check():
        """Endpoint para verificar se a API está funcionando"""
        return jsonify({
            'status': 'ok',
            'service': 'Sistema Ágil - Vistoria',
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Página de erro 404"""
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Página de erro 500"""
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Por favor, tente novamente mais tarde'
        }), 500
    
    return app

def open_browser():
    """Abrir navegador após o servidor estar pronto"""
    time.sleep(1.5)  # Aguardar servidor iniciar
    try:
        webbrowser.open('http://localhost:5000')
    except:
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
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
