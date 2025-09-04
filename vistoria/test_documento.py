#!/usr/bin/env python3
"""
Teste para verificar fluxo de documentos
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import get_vistoria_db
from utils.photo_utils import process_vistoria_photos

def test_documento_flow():
    """Testar fluxo completo de documentos"""
    print("🧪 TESTE: Iniciando teste de documentos...")
    
    # Dados simulados de um documento (PDF simples em base64)
    # Criando um PDF mínimo válido em base64
    import base64
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n253\n%%EOF'
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    test_document = {
        'category': 'documento_nota_fiscal',
        'name': 'documento_nota_fiscal',
        'url': f'data:application/pdf;base64,{pdf_base64}',
        'size': len(pdf_content),
        'type': 'application/pdf'
    }
    
    print(f"🔍 TESTE: Documento simulado: {test_document}")
    
    # Criar uma vistoria de teste (usando ID existente)
    vistoria_id = 1  # ID da vistoria existente
    vistoria_token = "VIST_A89SLU03IZXW_20250904_120112"  # Token existente
    
    # Testar processo
    try:
        foto_ids = process_vistoria_photos([test_document], vistoria_id, vistoria_token)
        print(f"✅ TESTE: Resultado do processo: {foto_ids}")
        
        if foto_ids and foto_ids[0]:
            print(f"✅ TESTE: Documento inserido com sucesso! ID: {foto_ids[0]}")
        else:
            print(f"❌ TESTE: Falha ao inserir documento")
        
        # Verificar no banco
        vistoria_db = get_vistoria_db()
        conn = vistoria_db.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM fotos_vistoria WHERE tipo = 'documento'")
        doc_count = cursor.fetchone()
        print(f"📊 TESTE: Total de documentos no banco após teste: {doc_count['total']}")
        
        vistoria_db.db_manager.return_connection(conn)
        
    except Exception as e:
        print(f"❌ TESTE: Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_documento_flow()
