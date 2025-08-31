#!/usr/bin/env python3
"""
Script para executar as alterações na tabela vistorias
Adiciona os novos campos: km_rodado e documento_nota_fiscal
"""

import sys
import os

# Adicionar o diretório pai ao path para importar modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseConfig
import psycopg2

def execute_sql_file(sql_file_path):
    """Executar arquivo SQL"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DatabaseConfig.get_connection_params())
        cursor = conn.cursor()
        
        # Ler arquivo SQL
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Executar comandos
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Alterações na tabela executadas com sucesso!")
        
        # Verificar se as colunas foram criadas
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'vistorias' 
            AND column_name IN ('km_rodado', 'documento_nota_fiscal')
            ORDER BY column_name;
        """)
        
        results = cursor.fetchall()
        if results:
            print("\n📋 Novas colunas criadas:")
            for row in results:
                print(f"   - {row[0]} ({row[1]}) - Nullable: {row[2]}")
        else:
            print("⚠️ Nenhuma coluna nova encontrada. Verifique se já existiam.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao executar SQL: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Caminho do arquivo SQL
    sql_file = os.path.join(os.path.dirname(__file__), 'add_new_columns.sql')
    
    print("🚀 Executando alterações na tabela vistorias...")
    print(f"📁 Arquivo SQL: {sql_file}")
    
    if not os.path.exists(sql_file):
        print(f"❌ Arquivo SQL não encontrado: {sql_file}")
        sys.exit(1)
    
    success = execute_sql_file(sql_file)
    
    if success:
        print("\n🎉 Banco de dados atualizado com sucesso!")
        print("   Os novos campos estão prontos para uso:")
        print("   - km_rodado: Para quilometragem do veículo")
        print("   - documento_nota_fiscal: Para caminho do arquivo")
    else:
        print("\n💥 Falha ao atualizar banco de dados!")
        sys.exit(1)
