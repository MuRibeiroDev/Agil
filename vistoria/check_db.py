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
    
    db.db_manager.return_connection(conn)
    print("Conexão retornada ao pool com sucesso")
    
except Exception as e:
    print(f'Erro: {e}')
    print("Traceback completo:")
    traceback.print_exc()
