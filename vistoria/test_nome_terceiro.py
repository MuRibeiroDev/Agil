#!/usr/bin/env python3
from db import get_vistoria_db

def test_nome_terceiro():
    """Teste para verificar o campo nome_terceiro no banco"""
    db = get_vistoria_db()
    
    # Buscar a vistoria mais recente
    conn = db.db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, token, nome_cliente, nome_terceiro, proprio FROM vistorias ORDER BY id DESC LIMIT 5')
    vistorias = cursor.fetchall()
    
    print("🔍 Verificando campos de nome nas últimas 5 vistorias:")
    for v in vistorias:
        vistoria_dict = dict(v)
        print(f"ID: {vistoria_dict['id']}, Token: {vistoria_dict['token']}")
        print(f"  nome_cliente: '{vistoria_dict.get('nome_cliente')}'")
        print(f"  nome_terceiro: '{vistoria_dict.get('nome_terceiro')}'")
        print(f"  proprio: {vistoria_dict.get('proprio')}")
        print("")
    
    db.db_manager.return_connection(conn)

if __name__ == '__main__':
    test_nome_terceiro()
