"""
Rotas de autenticação
"""
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
from config import load_users_from_env

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    """Tela de login"""
    return render_template('login.html')


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API para fazer login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        nome = data.get('nome_vistoriador', '').strip()
        codigo = data.get('codigo_acesso', '').strip()
        
        if not nome or not codigo:
            return jsonify({
                'success': False,
                'message': 'Nome e código são obrigatórios'
            }), 400
        
        # Carregar usuários do arquivo .env
        usuarios_autorizados = load_users_from_env()
        
        # Verificar credenciais
        if codigo in usuarios_autorizados and usuarios_autorizados[codigo].lower() == nome.lower():
            # Criar sessão
            session['vistoriador'] = {
                'nome': usuarios_autorizados[codigo],
                'login_time': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso',
                'vistoriador': usuarios_autorizados[codigo]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nome ou código incorretos'
            }), 401
    
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API para fazer logout"""
    try:
        session.pop('vistoriador', None)
        
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        })
    
    except Exception as e:
        print(f"❌ Erro no logout: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500


@auth_bp.route('/api/check-session')
def check_session():
    """Verificar se o usuário está logado"""
    try:
        vistoriador = session.get('vistoriador')
        
        if vistoriador:
            # Verificar se a sessão não expirou (24 horas)
            login_time = datetime.fromisoformat(vistoriador['login_time'])
            if datetime.now() - login_time > timedelta(hours=24):
                # Sessão expirada
                session.pop('vistoriador', None)
                return jsonify({
                    'logged_in': False,
                    'message': 'Sessão expirada'
                })
            
            return jsonify({
                'logged_in': True,
                'vistoriador': vistoriador['nome']
            })
        else:
            return jsonify({
                'logged_in': False,
                'message': 'Não logado'
            })
    
    except Exception as e:
        print(f"❌ Erro ao verificar sessão: {e}")
        return jsonify({
            'logged_in': False,
            'message': 'Erro interno'
        }), 500


def require_login(f):
    """Decorator para rotas que requerem login"""
    def decorated_function(*args, **kwargs):
        vistoriador = session.get('vistoriador')
        if not vistoriador:
            return redirect(url_for('auth.login'))
        
        # Verificar se a sessão não expirou
        login_time = datetime.fromisoformat(vistoriador['login_time'])
        if datetime.now() - login_time > timedelta(hours=24):
            session.pop('vistoriador', None)
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function
