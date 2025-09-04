from db.database import get_vistoria_db

try:
    print("Verificando vistorias existentes...")
    db = get_vistoria_db()
    conn = db.db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, token, placa, modelo FROM vistorias ORDER BY id DESC LIMIT 5')
    vistorias = cursor.fetchall()
    
    if vistorias:
        print(f"Encontradas {len(vistorias)} vistorias:")
        for v in vistorias:
            print(f"  ID: {v['id']}, Token: {v['token']}, Placa: {v['placa']}, Modelo: {v['modelo']}")
    else:
        print("Nenhuma vistoria encontrada")
    
    db.db_manager.return_connection(conn)
    
except Exception as e:
    print(f"Erro: {e}")
