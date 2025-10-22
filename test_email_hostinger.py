"""
Teste de envio de email com Hostinger
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.email_sender import EmailSender
from config.config import RECIPIENTS
from datetime import datetime

def test_email():
    """Testa envio de email simples com Hostinger"""
    try:
        print("=" * 70)
        print("  TESTE DE EMAIL - HOSTINGER")
        print("=" * 70)
        
        print("\n[1/3] Configurando EmailSender...")
        sender = EmailSender()
        
        print(f"  SMTP Server: {sender.smtp_server}")
        print(f"  SMTP Port: {sender.smtp_port}")
        print(f"  Sender Email: {sender.sender_email}")
        print(f"  Use SSL: {sender.use_ssl}")
        print(f"  Use TLS: {sender.use_tls}")
        
        print("\n[2/3] Preparando email de teste...")
        
        subject = f"Teste de Email - Sistema UTC Weather Reports - {datetime.now().strftime('%H:%M:%S')}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .success {{
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .info {{
                    background-color: #cfe2ff;
                    border: 1px solid #b6d4fe;
                    color: #084298;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Email de Teste</h1>
                    <p>Sistema UTC Weather Reports</p>
                </div>
                <div class="content">
                    <h2>🎉 Teste de Envio de Email</h2>
                    
                    <div class="success">
                        <strong>✅ Sucesso!</strong><br>
                        Se você está lendo este email, significa que o sistema de envio está funcionando corretamente!
                    </div>
                    
                    <div class="info">
                        <strong>📧 Informações do Teste:</strong><br>
                        <strong>Servidor SMTP:</strong> smtp.hostinger.com<br>
                        <strong>Porta:</strong> 465 (SSL)<br>
                        <strong>Horário do Teste:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br>
                        <strong>Remetente:</strong> no-reply@rezum.me
                    </div>
                    
                    <p>
                        Este é um email de teste automático enviado pelo sistema 
                        <strong>UTC Weather Reports</strong> para verificar a configuração 
                        do servidor de email Hostinger.
                    </p>
                    
                    <p>
                        O sistema está pronto para enviar relatórios de previsão de tempo 
                        com dados REAIS da WeatherAPI.com em Português! 🌍
                    </p>
                    
                    <div class="footer">
                        <p><strong>Sistema UTC Weather Reports</strong></p>
                        <p>Disciplina: Banco de Dados | Projeto Acadêmico</p>
                        <p>Este é um email automático de teste. Não responda.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        print(f"\n[3/3] Enviando email para {len(RECIPIENTS)} destinatário(s)...")
        for recipient in RECIPIENTS:
            print(f"  → {recipient}")
        
        print("\nEnviando... (aguarde)")
        
        result = sender.send_report_email(
            recipients=RECIPIENTS,
            subject=subject,
            html_body=html_body,
            report_file_path=None
        )
        
        print("\n" + "=" * 70)
        if result['success']:
            print("  ✅ EMAIL ENVIADO COM SUCESSO!")
            print("=" * 70)
            print(f"\nMensagem: {result['message']}")
            print(f"Horário: {result['timestamp'].strftime('%H:%M:%S')}")
            print(f"\n📬 Verifique a caixa de entrada dos destinatários:")
            for recipient in RECIPIENTS:
                print(f"  • {recipient}")
            print("\n⚠️ Nota: O email pode estar na pasta de SPAM/LIXO ELETRÔNICO")
            print("=" * 70)
            return True
        else:
            print("  ❌ FALHA AO ENVIAR EMAIL")
            print("=" * 70)
            print(f"\nErro: {result['message']}")
            print(f"Horário: {result['timestamp'].strftime('%H:%M:%S')}")
            print("\n🔧 Verifique:")
            print("  • Email e senha corretos em config.py")
            print("  • Conexão com internet")
            print("  • Configurações do servidor SMTP")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    if test_email():
        sys.exit(0)
    else:
        sys.exit(1)
