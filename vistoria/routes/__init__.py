"""
Rotas da aplicação
"""
# Imports comentados temporariamente para evitar problemas circulares
# from .vistoria_routes import vistoria_bp
# from .assinatura_routes import assinatura_bp
# from .api_routes import api_bp

# Para resolver imports circulares, vamos importar diretamente onde necessário
def get_blueprints():
    """Retorna os blueprints quando necessário"""
    from .vistoria_routes import vistoria_bp
    from .assinatura_routes import assinatura_bp
    from .api_routes import api_bp
    return vistoria_bp, assinatura_bp, api_bp

__all__ = ['get_blueprints']
