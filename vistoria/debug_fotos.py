#!/usr/bin/env python3
from db import get_vistoria_db

def debug_fotos():
    db = get_vistoria_db()
    # Buscar vistorias recentes
    conn = db.db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, token, nome_cliente, nome_terceiro, proprio FROM vistorias ORDER BY id DESC LIMIT 3')
    vistorias = cursor.fetchall()
    
    print("🔍 Verificando campos de nome nas últimas 3 vistorias:")
    for v in vistorias:
        vistoria_dict = dict(v)
        print(f'Vistoria ID: {vistoria_dict["id"]}, Token: {vistoria_dict["token"]}')
        print(f'  nome_cliente: "{vistoria_dict.get("nome_cliente")}"')
        print(f'  nome_terceiro: "{vistoria_dict.get("nome_terceiro")}"')
        print(f'  proprio: {vistoria_dict.get("proprio")}')
        print('')
    
    db.db_manager.return_connection(conn)

if __name__ == '__main__':
    debug_fotos()

if __name__ == '__main__':
    debug_fotos()
