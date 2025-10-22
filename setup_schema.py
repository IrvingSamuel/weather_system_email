"""
Script para executar automaticamente o schema do PostgreSQL
Conecta ao banco e cria todas as tabelas necessárias
"""

import sys
import psycopg2
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import DB_CONFIG

def execute_schema():
    """Executa o schema PostgreSQL automaticamente"""
    
    schema_file = Path(__file__).parent / 'database' / 'schema_postgresql.sql'
    
    if not schema_file.exists():
        print(f"❌ Erro: Arquivo schema não encontrado: {schema_file}")
        return False
    
    try:
        print("🔄 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        
        print("📖 Lendo schema...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Remover linhas de CREATE DATABASE e comentários iniciais
        lines = []
        skip = False
        for line in schema_sql.split('\n'):
            # Pular CREATE DATABASE
            if 'CREATE DATABASE' in line or 'ENCODING' in line or 'LOCALE' in line:
                skip = True
            elif skip and (line.strip() == ';' or line.strip() == ''):
                skip = False
                continue
            
            # Pular conectar ao banco
            if '\\c utc_weather_db' in line:
                continue
                
            if not skip:
                lines.append(line)
        
        schema_sql = '\n'.join(lines)
        
        print("⚙️  Executando schema...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema executado com sucesso!")
        
        # Verificar tabelas criadas
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        table_count = cur.fetchone()[0]
        print(f"✅ Total de {table_count} tabelas criadas")
        
        # Listar tabelas
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print("\n📋 Tabelas criadas:")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro PostgreSQL: {str(e)[:150]}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {str(e)[:150]}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🗄️  Setup Automático do Schema PostgreSQL")
    print("="*60 + "\n")
    
    success = execute_schema()
    
    if success:
        print("\n" + "="*60)
        print("  ✅ SUCESSO! Schema configurado")
        print("="*60 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("  ❌ FALHA! Verifique os erros acima")
        print("="*60 + "\n")
        sys.exit(1)
