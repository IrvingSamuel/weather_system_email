#!/usr/bin/env python
"""
Script de Setup - UTC Weather Reports
Configura e inicializa o projeto
"""

import os
import sys
import subprocess

def print_header(text):
    """Exibe cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Verifica versão do Python"""
    print_header("Verificando Versão do Python")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é requerido!")
        return False
    
    print("✅ Versão do Python compatível")
    return True

def install_requirements():
    """Instala pacotes Python"""
    print_header("Instalando Dependências Python")
    
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            "requirements.txt"
        ])
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print_header("Criando Diretórios")
    
    directories = [
        'logs',
        'reports',
        'templates',
        'database'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório {directory}/ criado/verificado")
    
    return True

def configure_database():
    """Guia para configurar banco de dados"""
    print_header("Configuração do Banco de Dados")
    
    print("""
    Para configurar o banco de dados MySQL:
    
    1. Abra o MySQL Workbench ou use o command line:
       mysql -u root -p
    
    2. Execute o script SQL:
       source database/schema.sql
    
    3. Edite config/config.py com suas credenciais:
       - host: localhost ou seu servidor
       - user: seu usuário MySQL
       - password: sua senha MySQL
    
    4. Crie um banco de dados: utc_weather_db
    """)
    
    input("\nPressione Enter após configurar o banco de dados...")
    return True

def configure_email():
    """Guia para configurar email"""
    print_header("Configuração de Email")
    
    print("""
    Para enviar emails:
    
    1. Se usar Gmail:
       - Ativar 2FA em conta Google
       - Gerar "Senha de Aplicativo" (não sua senha normal)
       - Usar 'SMTP_PASSWORD' = sua senha de app
    
    2. Se usar outro provider:
       - Verificar servidor SMTP
       - Porta padrão: 587 (TLS)
    
    3. Edite config/config.py:
       EMAIL_CONFIG = {
           'sender_email': 'seu_email@gmail.com',
           'sender_password': 'sua_senha_app'
       }
    
    4. Adicione destinatários em RECIPIENTS
    """)
    
    input("\nPressione Enter após configurar email...")
    return True

def test_database_connection():
    """Testa conexão com banco de dados"""
    print_header("Testando Conexão com Banco de Dados")
    
    try:
        from src.database import DatabaseConnection
        
        db = DatabaseConnection()
        if db.connection:
            print("✅ Conexão com banco de dados bem-sucedida!")
            
            # Verificar tabelas
            tables = db.fetch_query("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'utc_weather_db'
            """)
            
            if tables:
                print(f"✅ Total de {len(tables)} tabelas encontradas:")
                for table in tables:
                    print(f"   - {table['TABLE_NAME']}")
            
            db.disconnect()
            return True
        else:
            print("❌ Falha ao conectar ao banco de dados")
            print("Verifique as credenciais em config/config.py")
            return False
    
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        print("Certifique-se de que MySQL está instalado e rodando")
        return False

def test_email():
    """Testa envio de email"""
    print_header("Testando Envio de Email")
    
    try:
        from src.email_sender import EmailSender
        from config.config import EMAIL_CONFIG
        
        sender = EmailSender()
        
        print("Testando conexão SMTP...")
        
        # Testa conexão
        import smtplib
        server = smtplib.SMTP(sender.smtp_server, sender.smtp_port)
        server.starttls()
        server.login(sender.sender_email, sender.sender_password)
        server.quit()
        
        print("✅ Configuração de email válida!")
        
        confirm = input("\nDeseja enviar um email de teste? (s/n): ").lower()
        if confirm == 's':
            test_email_sent = sender.send_report_email(
                recipients=[sender.sender_email],
                subject="[TESTE] Relatório de UTCs - Email de Teste",
                html_body="<h1>Email de Teste</h1><p>Se você recebeu este email, o sistema de envio está funcionando!</p>"
            )
            
            if test_email_sent['success']:
                print(f"✅ Email de teste enviado para {sender.sender_email}")
            else:
                print(f"❌ Erro ao enviar email de teste: {test_email_sent['message']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro na configuração de email: {e}")
        print("Verifique suas credenciais de email")
        return False

def display_final_instructions():
    """Exibe instruções finais"""
    print_header("Instalação Concluída! 🎉")
    
    print("""
    Próximas Etapas:
    
    1. Verificar configurações:
       - config/config.py (Banco de dados e Email)
    
    2. Executar a aplicação:
       python -m src.main
    
    3. Menu de opções:
       1. Gerar Relatório
       2. Enviar Email
       3. Atualizar Previsão
       4. Ver Status de Jobs
       5. Limpar Logs
       6. Iniciar Scheduler Automático
       7. Parar Scheduler
       8. Sair
    
    4. Documentação:
       Leia README.md para detalhes completos
    
    Suporte:
    - Email: sync.irvingsamuel@gmail.com
    - Professor: francisco.vital@unima.edu.br
    """)

def main():
    """Função principal"""
    try:
        print("\n" + "="*60)
        print("  🌍 UTC Weather Reports - Setup Inicial")
        print("="*60)
        
        # Verificar Python
        if not check_python_version():
            sys.exit(1)
        
        # Criar diretórios
        if not create_directories():
            sys.exit(1)
        
        # Instalar dependências
        if not install_requirements():
            sys.exit(1)
        
        # Configurar banco de dados
        if not configure_database():
            sys.exit(1)
        
        # Testar conexão com BD
        if not test_database_connection():
            print("⚠️  Aviso: Verifique a configuração do banco de dados")
        
        # Configurar email
        if not configure_email():
            sys.exit(1)
        
        # Testar email
        if not test_email():
            print("⚠️  Aviso: Verifique a configuração de email")
        
        # Exibir instruções finais
        display_final_instructions()
        
        print("\n✅ Setup concluído com sucesso!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
