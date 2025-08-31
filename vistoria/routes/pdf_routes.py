"""
Rotas para geração e download de PDF
"""
import os
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from db import get_vistoria_db
from utils.pdf_utils import generate_vistoria_pdf

pdf_bp = Blueprint('pdf', __name__)


@pdf_bp.route('/api/gerar_pdf/<token>', methods=['GET'])
def gerar_pdf_vistoria(token):
    """Gerar e retornar PDF da vistoria"""
    try:
        print(f"📄 Gerando PDF para token: {token}")
        
        # Buscar dados da vistoria no banco
        db = get_vistoria_db()
        vistoria = db.buscar_vistoria_por_token(token)
        
        if not vistoria:
            return jsonify({
                'success': False,
                'message': 'Vistoria não encontrada'
            }), 404
        
        print(f"✅ Vistoria encontrada: ID {vistoria.get('id')}")
        
        # Debug: Mostrar campos da assinatura
        print(f"🖊️ DEBUG - Campos de assinatura:")
        for k, v in vistoria.items():
            if any(word in k.lower() for word in ['assinatura', 'cliente']):
                print(f"   {k}: {v}")
        
        # Buscar fotos da vistoria
        fotos = db.buscar_fotos_vistoria(vistoria['id'])
        print(f"📸 Fotos encontradas: {len(fotos)}")
        
        # Debug: Mostrar detalhes das fotos
        for i, foto in enumerate(fotos):
            print(f"   Foto {i+1}: {foto.get('categoria')} - {foto.get('arquivo_nome')}")
        
        # Preparar dados para o PDF
        pdf_data = {
            'token': vistoria.get('token'),
            'nome_cliente': vistoria.get('nome_cliente'),
            'nome_conferente': vistoria.get('nome_conferente'),
            'data_vistoria': vistoria.get('criado_em'),
            'status': vistoria.get('status'),
            'veiculo': {
                'placa': vistoria.get('placa'),
                'modelo': vistoria.get('modelo'),
                'cor': vistoria.get('cor'),
                'ano': str(vistoria.get('ano')) if vistoria.get('ano') else None,
                'km_rodado': vistoria.get('km_rodado')
            },
            'pneus': {
                'marca_pneu_dianteiro_esquerdo': vistoria.get('marca_pneu_dianteiro_esquerdo'),
                'marca_pneu_dianteiro_direito': vistoria.get('marca_pneu_dianteiro_direito'),
                'marca_pneu_traseiro_esquerdo': vistoria.get('marca_pneu_traseiro_esquerdo'),
                'marca_pneu_traseiro_direito': vistoria.get('marca_pneu_traseiro_direito')
            },
            'photos': [{'category': foto.get('categoria'), 'name': foto.get('arquivo_nome'), 'path': foto.get('arquivo_path')} for foto in fotos],
            'assinado_em': vistoria.get('assinatura_data'),
            'assinatura_path': vistoria.get('assinatura_arquivo_path'),
            'assinatura_checksum': vistoria.get('assinatura_checksum'),
            'cliente_nome_assinatura': vistoria.get('assinatura_cliente_nome')
        }
        
        # Adicionar campos do questionário
        questionnaire_fields = [
            'ar_condicionado', 'antenas', 'tapetes', 'tapete_porta_malas', 'bateria',
            'retrovisor_direito', 'retrovisor_esquerdo', 'extintor', 'roda_comum', 'roda_especial',
            'chave_principal', 'chave_reserva', 'manual', 'documento', 'nota_fiscal',
            'limpador_dianteiro', 'limpador_traseiro', 'triangulo', 'macaco', 'chave_roda', 'pneu_step'
        ]
        
        for field in questionnaire_fields:
            pdf_data[field] = vistoria.get(field, False)
        
        # Adicionar observações
        for i in range(1, 5):
            obs_field = f'desc_obs_{i}'
            pdf_data[obs_field] = vistoria.get(obs_field, '')
        
        # Criar diretório para PDFs se não existir
        pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nome do arquivo PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f'vistoria_{token}_{timestamp}.pdf'
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # Gerar PDF
        print(f"📄 Gerando PDF: {pdf_path}")
        success = generate_vistoria_pdf(pdf_data, pdf_path)
        
        if success and os.path.exists(pdf_path):
            print(f"✅ PDF gerado com sucesso: {pdf_filename}")
            
            # Retornar o arquivo PDF
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'Vistoria_{vistoria.get("placa", token)}.pdf',
                mimetype='application/pdf'
            )
        else:
            print(f"❌ Falha ao gerar PDF")
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar PDF'
            }), 500
    
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@pdf_bp.route('/api/pdf_info/<token>', methods=['GET'])
def obter_info_pdf(token):
    """Obter informações para geração de PDF"""
    try:
        # Buscar dados da vistoria no banco
        db = get_vistoria_db()
        vistoria = db.buscar_vistoria_por_token(token)
        
        if not vistoria:
            return jsonify({
                'success': False,
                'message': 'Vistoria não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'token': vistoria.get('token'),
                'cliente': vistoria.get('nome_cliente'),
                'placa': vistoria.get('placa'),
                'modelo': vistoria.get('modelo'),
                'status': vistoria.get('status')
            }
        })
    
    except Exception as e:
        print(f"❌ Erro ao obter info PDF: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
