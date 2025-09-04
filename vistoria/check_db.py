from db.database import get_vistoria_db
import traceback

try:
    print("Iniciando verificação do banco...")
    db = get_vistoria_db()
    print("Database manager obtido com sucesso")
    
    conn = db.db_manager.get_connection()
    print("Conexão estabelecida com sucesso")
    
    cursor = conn.cursor()
    print("Cursor criado com sucesso")
    
    # Verificar estrutura da tabela
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'vistorias' 
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print(f'Encontradas {len(columns)} colunas na tabela vistorias:')
    for col in columns:
        print(f'  - {col["column_name"]} ({col["data_type"]}) - Nullable: {col["is_nullable"]}')
    
    # Verificar se nome_cliente existe
    nome_cliente_exists = any(col["column_name"] == 'nome_cliente' for col in columns)
    print(f'\nColuna nome_cliente existe: {nome_cliente_exists}')
    
    # Verificar tabela fotos_vistoria
    print(f'\n{"="*50}')
    print("Verificando tabela fotos_vistoria...")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'fotos_vistoria' 
        ORDER BY ordinal_position;
    """)
    
    foto_columns = cursor.fetchall()
    if foto_columns:
        print(f'Encontradas {len(foto_columns)} colunas na tabela fotos_vistoria:')
        for col in foto_columns:
            print(f'  - {col["column_name"]} ({col["data_type"]}) - Nullable: {col["is_nullable"]}')
    else:
        print("❌ Tabela fotos_vistoria NÃO existe!")
    
    # Verificar se existem documentos salvos
    print(f'\n{"="*50}')
    print("Verificando documentos existentes...")
    try:
        cursor.execute("SELECT COUNT(*) as total FROM fotos_vistoria WHERE tipo = 'documento'")
        doc_count = cursor.fetchone()
        print(f"📄 Documentos encontrados no banco: {doc_count['total']}")
        
        cursor.execute("SELECT vistoria_id, categoria, arquivo_nome, arquivo_tamanho FROM fotos_vistoria WHERE tipo = 'documento' LIMIT 5")
        docs = cursor.fetchall()
        if docs:
            print("📄 Últimos documentos:")
            for doc in docs:
                print(f"  - Vistoria {doc['vistoria_id']}: {doc['categoria']} - {doc['arquivo_nome']} ({doc['arquivo_tamanho']} bytes)")
    except Exception as e:
        print(f"❌ Erro ao verificar documentos: {e}")
    
    db.db_manager.return_connection(conn)
    print("Conexão retornada ao pool com sucesso")
    
except Exception as e:
    print(f'Erro: {e}')
    print("Traceback completo:")
    traceback.print_exc()
