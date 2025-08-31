#!/usr/bin/env python3
"""
Script simples para testar se as colunas foram criadas
"""

import sys
import os

# Adicionar o diretório pai ao path para importar modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseConfig
import psycopg2

def test_columns():
    """Testar se as colunas existem"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DatabaseConfig.get_connection_params())
        cursor = conn.cursor()
        
        # Verificar colunas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vistorias' 
            AND column_name IN ('km_rodado', 'documento_nota_fiscal')
            ORDER BY column_name;
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("✅ Colunas encontradas:")
            for row in results:
                print(f"   - {row[0]} ({row[1]})")
            return True
        else:
            print("❌ Colunas não encontradas. Vou tentar criar...")
            
            # Tentar criar as colunas
            try:
                cursor.execute("ALTER TABLE vistorias ADD COLUMN IF NOT EXISTS km_rodado VARCHAR(50);")
                cursor.execute("ALTER TABLE vistorias ADD COLUMN IF NOT EXISTS documento_nota_fiscal TEXT;")
                conn.commit()
                print("✅ Colunas criadas com sucesso!")
                return True
            except Exception as e:
                print(f"❌ Erro ao criar colunas: {e}")
                return False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando colunas na tabela vistorias...")
    
    if test_columns():
        print("\n🎉 Banco está pronto para os novos campos!")
    else:
        print("\n💥 Problema com o banco de dados!")
        sys.exit(1)
