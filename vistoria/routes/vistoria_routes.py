"""
Rotas principais da vistoria
"""
from flask import Blueprint, render_template, send_from_directory, session
from routes.auth_routes import require_login

vistoria_bp = Blueprint('vistoria', __name__)


@vistoria_bp.route('/')
@require_login
def index():
    """Página principal da vistoria"""
    return render_template('index.html')


@vistoria_bp.route('/frontend/<path:filename>')
def frontend_static(filename):
    """Servir arquivos estáticos com prefixo /frontend/"""
    return send_from_directory('.', filename)


@vistoria_bp.route('/assets/<path:filename>')
def assets_static(filename):
    """Servir arquivos da pasta assets (favicon, etc.)"""
    response = send_from_directory('assets', filename)
    # Adicionar headers de cache para assets
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 ano
    return response


@vistoria_bp.route('/uploads/<path:filename>')
def uploaded_files(filename):
    """Servir arquivos de upload com cache headers"""
    response = send_from_directory('uploads', filename)
    # Adicionar headers de cache para performance
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 ano
    return response


@vistoria_bp.route('/assinaturas/<path:filename>')
def signature_files(filename):
    """Servir arquivos de assinatura com cache headers"""
    response = send_from_directory('assinaturas', filename)
    # Cache menos agressivo para assinaturas
    response.headers['Cache-Control'] = 'private, max-age=86400'  # 1 dia
    return response


@vistoria_bp.errorhandler(404)
def not_found(error):
    """Página de erro 404"""
    return render_template('index.html'), 404


@vistoria_bp.errorhandler(500)
def internal_error(error):
    """Página de erro 500"""
    return {
        'error': 'Erro interno do servidor',
        'message': 'Por favor, tente novamente mais tarde'
    }, 500
