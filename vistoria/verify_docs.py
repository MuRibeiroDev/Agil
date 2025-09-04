from db.database import get_vistoria_db

try:
    print("Verificando documentos no banco...")
    db = get_vistoria_db()
    conn = db.db_manager.get_connection()
    cursor = conn.cursor()
    
    # Buscar documentos existentes
    cursor.execute("""
        SELECT f.id, f.vistoria_id, f.categoria, f.tipo, f.arquivo_nome, 
               f.arquivo_tamanho, v.placa, v.modelo, v.criado_em
        FROM fotos_vistoria f
        JOIN vistorias v ON f.vistoria_id = v.id
        WHERE f.tipo = 'documento'
        ORDER BY f.id DESC
        LIMIT 10
    """)
    
    documentos = cursor.fetchall()
    
    if documentos:
        print(f"Encontrados {len(documentos)} documentos:")
        for doc in documentos:
            print(f"  ID: {doc['id']}, Vistoria: {doc['vistoria_id']} ({doc['placa']} - {doc['modelo']})")
            print(f"      Arquivo: {doc['arquivo_nome']} ({doc['arquivo_tamanho']} bytes)")
            print(f"      Data: {doc['criado_em']}")
            print()
    else:
        print("Nenhum documento encontrado no banco")
    
    db.db_manager.return_connection(conn)
    
except Exception as e:
    print(f"Erro: {e}")
