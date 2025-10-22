"""
Teste Completo do Sistema
Valida todos os componentes funcionam corretamente
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Adicionar ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print_header("1️⃣  TESTANDO IMPORTS")
    
    tests = [
        ("PyQt5", lambda: __import__('PyQt5')),
        ("psycopg2", lambda: __import__('psycopg2')),
        ("APScheduler", lambda: __import__('apscheduler')),
        ("Jinja2", lambda: __import__('jinja2')),
        ("src.database", lambda: __import__('src.database', fromlist=[''])),
        ("src.gui", lambda: __import__('src.gui', fromlist=[''])),
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print(f"  ✅ {name} - OK")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name} - ERRO: {str(e)[:40]}")
    
    return passed == len(tests)

def test_files():
    """Testa se todos os arquivos necessários existem"""
    print_header("2️⃣  TESTANDO ARQUIVOS")
    
    required_files = [
        'config/config.py',
        'database/schema_postgresql.sql',
        'src/gui.py',
        'src/main.py',
        'src/database.py',
        'src/report_generator.py',
        'src/email_sender.py',
        'src/scheduler.py',
        'requirements.txt',
    ]
    
    passed = 0
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path} - Encontrado")
            passed += 1
        else:
            print(f"  ❌ {file_path} - NÃO ENCONTRADO")
    
    return passed == len(required_files)

def test_database():
    """Testa conexão com banco de dados"""
    print_header("3️⃣  TESTANDO BANCO DE DADOS")
    
    try:
        import psycopg2
        from config.config import DB_CONFIG
        
        print(f"  Conectando a: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"  Database: {DB_CONFIG['database']}")
        print(f"  User: {DB_CONFIG['user']}")
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Testar query simples
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            
            print(f"  ✅ PostgreSQL: {version.split(',')[0]}")
            
            # Verificar se schema existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'utcs'
                );
            """)
            schema_exists = cur.fetchone()[0]
            
            if schema_exists:
                print(f"  ✅ Schema PostgreSQL - EXISTE")
                
                # Contar tabelas
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                table_count = cur.fetchone()[0]
                print(f"     Total de tabelas: {table_count}")
                
                passed = True
            else:
                print(f"  ⚠️  Schema PostgreSQL - NÃO ENCONTRADO")
                print(f"     ⚠️  EXECUTE: database/schema_postgresql.sql em pgAdmin!")
                passed = False
            
            cur.close()
            conn.close()
            
            return passed
            
        except psycopg2.OperationalError as e:
            print(f"  ❌ Erro de conexão: {str(e)[:50]}")
            print(f"  ⚠️  Verifique credenciais em config.py")
            print(f"  ⚠️  PostgreSQL está rodando?")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro geral: {str(e)}")
        return False

def test_directories():
    """Testa se todos os diretórios estão criados"""
    print_header("4️⃣  TESTANDO DIRETÓRIOS")
    
    required_dirs = ['src', 'config', 'database', 'logs', 'reports', 'venv']
    
    passed = 0
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ /{dir_name} - OK")
            passed += 1
        else:
            print(f"  ❌ /{dir_name} - NÃO ENCONTRADO")
    
    return passed == len(required_dirs)

def test_configuration():
    """Testa se a configuração está correta"""
    print_header("5️⃣  TESTANDO CONFIGURAÇÃO")
    
    try:
        from config.config import DB_CONFIG, EMAIL_CONFIG, RECIPIENTS, SELECTED_UTCS
        
        print(f"  ✅ DB_CONFIG:")
        print(f"     Host: {DB_CONFIG.get('host')}")
        print(f"     Port: {DB_CONFIG.get('port')}")
        print(f"     Database: {DB_CONFIG.get('database')}")
        print(f"     User: {DB_CONFIG.get('user')}")
        
        print(f"\n  ✅ EMAIL_CONFIG:")
        print(f"     SMTP Server: {EMAIL_CONFIG.get('smtp_server')}")
        print(f"     SMTP Port: {EMAIL_CONFIG.get('smtp_port')}")
        print(f"     From Email: {EMAIL_CONFIG.get('from_email')}")
        
        print(f"\n  ✅ RECIPIENTS:")
        for recipient in RECIPIENTS:
            print(f"     - {recipient}")
        
        print(f"\n  ✅ SELECTED_UTCS:")
        for utc in SELECTED_UTCS:
            print(f"     - {utc}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao ler configuração: {e}")
        return False

def test_gui_launch():
    """Testa se a GUI consegue ser importada"""
    print_header("6️⃣  TESTANDO GUI")
    
    try:
        from src.gui import MainWindow, Worker
        print(f"  ✅ GUI MainWindow - Importado")
        print(f"  ✅ GUI Worker Thread - Importado")
        print(f"  💡 Para iniciar a GUI, execute: python gui_launcher.py")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao importar GUI: {str(e)[:60]}")
        return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🧪 TESTE COMPLETO DO SISTEMA ".center(58) + "║")
    print("║" + "  UTC Weather Reports ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Arquivos", test_files()))
    results.append(("Diretórios", test_directories()))
    results.append(("Configuração", test_configuration()))
    results.append(("Banco de Dados", test_database()))
    results.append(("GUI", test_gui_launch()))
    
    # Resumo
    print_header("📊 RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"  Total: {passed}/{total} testes passou")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 TUDO FUNCIONANDO! Sua aplicação está pronta!\n")
        print("🚀 Para iniciar a GUI, execute:")
        print("   .\launch-gui-simple.ps1\n")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Veja erros acima.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
