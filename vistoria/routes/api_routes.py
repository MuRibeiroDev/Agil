"""
Rotas da API
"""
import json
from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_vistoria_db
from utils import save_uploaded_photo, save_signature_image, save_vistoria_complete
from .assinatura_routes import prepare_vistoria_data_for_saving

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/salvar_vistoria_completa', methods=['POST'])
def salvar_vistoria_completa():
    """API para salvar vistoria completa incluindo assinatura presencial"""
    try:
        # Obter dados JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400
        
        print(f"📋 Recebendo vistoria JSON: {data.get('veiculo', {}).get('placa', 'N/A')}")
        print(f"🔍 DADOS RECEBIDOS - Chaves principais: {list(data.keys())}")
        print(f"🔍 DADOS RECEBIDOS - Photos: {len(data.get('photos', []))} itens")
        if data.get('photos'):
            for i, photo in enumerate(data.get('photos', [])):
                print(f"   Photo {i+1}: category={photo.get('category')}, name={photo.get('name')}, type={photo.get('type')}")
        print(f"🔍 DADOS RECEBIDOS - Documento direto: {'presente' if data.get('documento') else 'ausente'}")
        print(f"🔍 DADOS RECEBIDOS - Assinatura: {'presente' if data.get('assinatura') else 'ausente'}")
        print(f"🔍 DEBUG: nome_cliente recebido: '{data.get('nome_cliente', 'AUSENTE')}'")
        print(f"🔍 DEBUG: nome_terceiro recebido: '{data.get('veiculo', {}).get('nome_terceiro', 'AUSENTE')}'")
        
        
        # Log completo apenas se necessário para debug (comentado para não sobrecarregar)
        # print(f"🔍 Dados completos recebidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Usar a função auxiliar para preparar os dados
        dados_convertidos = prepare_vistoria_data_for_saving(data)
        
        print(f"🔍 DEBUG: Dados dos pneus: {dados_convertidos['pneus']}")
        
        # Adicionar questionário (mantém compatibilidade)
        questionario = data.get('questionario', {})
        for key, value in questionario.items():
            dados_convertidos[key] = value
        
        # CORREÇÃO: Adicionar campos de observação que estão no nível raiz
        for key, value in data.items():
            if key.startswith('desc_obs_'):
                dados_convertidos[key] = value
        
        # Processar fotos do formato JSON
        photos_data = []
        
        # PRIMEIRA PRIORIDADE: Array 'photos' (novo formato)
        photos_array = data.get('photos', [])
        print(f"🔍 PROCESSAMENTO: Array 'photos' contém {len(photos_array)} itens")
        for photo in photos_array:
            if photo and photo.get('url'):
                photos_data.append({
                    'category': photo.get('category'),
                    'name': photo.get('name'),
                    'url': photo.get('url'),
                    'size': photo.get('size', 0),
                    'type': photo.get('type', 'image/jpeg')
                })
                print(f"   ✅ Adicionada: {photo.get('category')} ({photo.get('type')})")
        
        # SEGUNDA PRIORIDADE: Objeto 'fotos' (formato antigo - fallback)
        if not photos_data:  # Só se não encontrou nada no array 'photos'
            fotos = data.get('fotos', {})
            print(f"🔍 FALLBACK: Objeto 'fotos' contém {len(fotos)} itens")
            for field_name, foto_data in fotos.items():
                if foto_data and foto_data.get('url'):
                    photos_data.append({
                        'category': field_name,
                        'name': field_name,
                        'url': foto_data['url'],
                        'size': foto_data.get('size', 0),
                        'type': foto_data.get('type', 'image/jpeg')
                    })
                    print(f"   ✅ Adicionada (fallback): {field_name}")
        
        print(f"🔍 TOTAL FINAL: {len(photos_data)} fotos serão processadas")
        dados_convertidos['photos'] = photos_data
        
        # Processar documento se fornecido
        documento = data.get('documento')
        if documento and documento.get('file'):
            # Aqui você pode implementar o upload do documento
            # Por enquanto, só armazenamos o nome
            dados_convertidos['veiculo']['documento_nota_fiscal'] = documento.get('name', '')
        
        # Salvar no banco de dados
        result = save_vistoria_complete(dados_convertidos)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar no banco: {result["error"]}'
            }), 500
        
        # Processar assinatura presencial se fornecida
        assinatura = data.get('assinatura')
        if assinatura:
            print("🖊️ Processando assinatura presencial...")
            
            # Salvar assinatura como arquivo
            signature_info = save_signature_image(assinatura, result['token'])
            
            if signature_info:
                # Atualizar vistoria no banco com assinatura
                vistoria_db = get_vistoria_db()
                assinatura_result = vistoria_db.atualizar_assinatura_vistoria(
                    token=result['token'],
                    assinatura_path=signature_info['path'],
                    cliente_nome=data.get('nome_conferente', 'Cliente'),
                    checksum=signature_info['checksum']
                )
                
                if assinatura_result:
                    print(f"✅ Assinatura presencial salva: {assinatura_result['placa']}")
                else:
                    print("⚠️ Erro ao salvar assinatura no banco")
            else:
                print("⚠️ Erro ao salvar arquivo de assinatura")
        
        return jsonify({
            'success': True,
            'message': 'Vistoria e assinatura salvadas com sucesso!',
            'id': result['vistoria_id'],
            'token': result['token']
        })
        
    except Exception as e:
        print(f"❌ Erro na API salvar_vistoria_completa: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@api_bp.route('/api/salvar_vistoria', methods=['POST'])
def salvar_vistoria():
    """API para salvar dados da vistoria no banco PostgreSQL (form-data)"""
    try:
        # Processar dados do formulário
        dados = request.form.to_dict()
        arquivos = request.files
        
        print(f"📋 Recebendo vistoria: {dados.get('placa', 'N/A')}")
        
        # Processar arquivos de upload
        photos_data = []
        for field_name, file in arquivos.items():
            if file and file.filename:
                # Salvar arquivo físico
                arquivo_info = save_uploaded_photo(file, field_name, 'temp')
                if arquivo_info:
                    photos_data.append({
                        'category': field_name,
                        'name': field_name,
                        'url': arquivo_info['url'],
                        'size': arquivo_info['size'],
                        'type': arquivo_info['mime_type']
                    })
        
        # Adicionar fotos aos dados
        dados['photos'] = photos_data
        
        # Salvar no banco de dados
        result = save_vistoria_complete(dados)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Vistoria salva com sucesso no banco de dados!',
                'id': result['vistoria_id'],
                'token': result['token']
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Erro ao salvar no banco: {result["error"]}'
            }), 500
        
    except Exception as e:
        print(f"❌ Erro na API salvar_vistoria: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@api_bp.route('/api/health')
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    try:
        # Testar conexão com banco
        vistoria_db = get_vistoria_db()
        db_status = "connected" if vistoria_db else "disconnected"
        
        return jsonify({
            'status': 'ok',
            'service': 'Sistema Ágil - Vistoria',
            'version': '2.0.0',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@api_bp.route('/api/vistorias')
def listar_vistorias():
    """Listar vistorias do banco de dados"""
    try:
        vistoria_db = get_vistoria_db()
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')
        
        offset = (page - 1) * per_page
        
        vistorias = vistoria_db.listar_vistorias_resumo(
            limit=per_page,
            offset=offset,
            status=status
        )
        
        return jsonify({
            'success': True,
            'total': len(vistorias),
            'page': page,
            'per_page': per_page,
            'vistorias': vistorias
        })
        
    except Exception as e:
        print(f"❌ Erro ao listar vistorias: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao listar: {str(e)}'
        }), 500


@api_bp.route('/api/vistoria/<vistoria_id>')
def obter_vistoria(vistoria_id):
    """Obter vistoria completa por ID"""
    try:
        vistoria_db = get_vistoria_db()
        
        # Buscar vistoria por ID (implementar se necessário)
        # Por enquanto, retornar erro
        return jsonify({
            'success': False,
            'message': 'Funcionalidade em desenvolvimento'
        }), 501
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500