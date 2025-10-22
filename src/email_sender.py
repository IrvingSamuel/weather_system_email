"""
Módulo de Envio de Emails
Gerencia envio de relatórios por email com autenticação segura
"""

import smtplib
import logging
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from config.config import EMAIL_CONFIG, RECIPIENTS, LOGGING_CONFIG

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    filename=LOGGING_CONFIG['file']
)
logger = logging.getLogger(__name__)

# Configurar timeout padrão para socket
socket.setdefaulttimeout(10)


class EmailSender:
    """Classe para enviar emails com relatórios"""
    
    def __init__(self):
        """Inicializa o enviador de emails"""
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.sender_email = EMAIL_CONFIG['sender_email']
        self.sender_password = EMAIL_CONFIG['sender_password']
        self.use_tls = EMAIL_CONFIG.get('use_tls', False)
        self.use_ssl = EMAIL_CONFIG.get('use_ssl', False)
    
    def send_report_email(self, recipients: List[str], subject: str, 
                         html_body: str, report_file_path: str = None,
                         utc_ids: List[int] = None) -> Dict[str, Any]:
        """
        Envia um email com o relatório em HTML
        
        Args:
            recipients: Lista de endereços de email dos destinatários
            subject: Assunto do email
            html_body: Corpo do email em HTML
            report_file_path: Caminho do arquivo de relatório para anexar
            utc_ids: Lista de IDs das UTCs incluídas no relatório
        
        Returns:
            Dict: Resultado do envio {'success': bool, 'message': str, 'timestamp': datetime}
        """
        try:
            # Criar mensagem multipart
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject
            
            # Adicionar corpo HTML
            html_part = MIMEText(html_body, 'html', 'utf-8')
            message.attach(html_part)
            
            # Anexar arquivo do relatório se fornecido
            if report_file_path and os.path.exists(report_file_path):
                try:
                    self._attach_file(message, report_file_path)
                    logger.info(f"Arquivo anexado: {report_file_path}")
                except Exception as e:
                    logger.warning(f"Erro ao anexar arquivo: {e}")
            
            # Conectar ao servidor SMTP e enviar COM TIMEOUT
            try:
                logger.info(f"Conectando a {self.smtp_server}:{self.smtp_port} com timeout 10s...")
                
                # Usar SMTP_SSL para porta 465 (Hostinger)
                if self.use_ssl:
                    logger.info("Usando SMTP_SSL (porta 465)...")
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
                else:
                    # Usar SMTP normal com STARTTLS para porta 587
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                    if self.use_tls:
                        logger.info("Iniciando TLS...")
                        server.starttls(timeout=10)
                
                logger.info(f"Fazendo login como {self.sender_email}...")
                server.login(self.sender_email, self.sender_password)
                
                logger.info(f"Enviando email para {len(recipients)} destinatario(s)...")
                for recipient in recipients:
                    try:
                        server.send_message(message)
                        logger.info(f"Email enviado com sucesso para: {recipient}")
                    except Exception as e:
                        logger.error(f"Erro ao enviar email para {recipient}: {e}")
                        server.quit()
                        return {
                            'success': False,
                            'message': f'Erro ao enviar para {recipient}: {str(e)[:100]}',
                            'timestamp': datetime.now(),
                            'utc_ids': utc_ids
                        }
                
                server.quit()
                
                result = {
                    'success': True,
                    'message': f'Email enviado com sucesso para {len(recipients)} destinatario(s)',
                    'timestamp': datetime.now(),
                    'recipients': recipients,
                    'utc_ids': utc_ids
                }
                
                logger.info(f"Email enviado com sucesso. Assunto: {subject}")
                return result
                
            except socket.timeout:
                logger.error("TIMEOUT ao conectar ao SMTP. Servidor nao respondeu.")
                return {
                    'success': False,
                    'message': 'TIMEOUT: Servidor SMTP nao respondeu em tempo',
                    'timestamp': datetime.now(),
                    'utc_ids': utc_ids
                }
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Erro de autenticacao SMTP: {e}")
                return {
                    'success': False,
                    'message': f'Erro de autenticacao: Verifique email e senha',
                    'timestamp': datetime.now(),
                    'utc_ids': utc_ids
                }
        
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return {
                'success': False,
                'message': f'Erro ao enviar email: {str(e)[:100]}',
                'timestamp': datetime.now(),
                'utc_ids': utc_ids
            }
    
    @staticmethod
    def _attach_file(message: MIMEMultipart, file_path: str) -> None:
        """
        Anexa um arquivo à mensagem
        
        Args:
            message: Mensagem MIME
            file_path: Caminho do arquivo
        """
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 
                       f'attachment; filename= {os.path.basename(file_path)}')
        message.attach(part)
    
    @staticmethod
    def create_html_email_body(utcs_data: List[Dict[str, Any]]) -> str:
        """
        Cria o corpo do email em HTML com dados das UTCs
        
        Args:
            utcs_data: Lista com dados das UTCs
        
        Returns:
            str: HTML do email
        """
        current_date = datetime.now().strftime("%d de %B de %Y")
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de UTCs - Previsão de Tempo</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                }}
                
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                
                .header h1 {{
                    margin: 0;
                    font-size: 1.8em;
                }}
                
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .greeting {{
                    margin-bottom: 25px;
                    font-size: 1.1em;
                }}
                
                .utc-card {{
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                
                .utc-card h3 {{
                    margin: 0 0 10px 0;
                    color: #667eea;
                    font-size: 1.3em;
                }}
                
                .utc-card p {{
                    margin: 8px 0;
                    font-size: 0.95em;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-top: 10px;
                }}
                
                .info-item {{
                    background: white;
                    padding: 8px;
                    border-radius: 4px;
                    border: 1px solid #e0e0e0;
                }}
                
                .info-item strong {{
                    color: #667eea;
                    display: block;
                    font-size: 0.8em;
                    text-transform: uppercase;
                }}
                
                .info-item span {{
                    display: block;
                    margin-top: 4px;
                    font-weight: 500;
                }}
                
                .weather-info {{
                    background: linear-gradient(135deg, #e3f2fd 0%, #e1f5fe 100%);
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
                
                .weather-info h4 {{
                    margin: 0 0 10px 0;
                    color: #01579b;
                }}
                
                .weather-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}
                
                .weather-item {{
                    background: white;
                    padding: 10px;
                    border-radius: 4px;
                    text-align: center;
                }}
                
                .weather-item div:first-child {{
                    font-size: 0.8em;
                    color: #666;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                
                .weather-item div:last-child {{
                    font-size: 1.1em;
                    font-weight: bold;
                    color: #01579b;
                }}
                
                .media-links {{
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #e0e0e0;
                }}
                
                .media-link {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-size: 0.85em;
                    margin-right: 8px;
                    margin-top: 5px;
                    transition: background 0.3s ease;
                }}
                
                .media-link:hover {{
                    background: #764ba2;
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 0.85em;
                    color: #666;
                    border-top: 1px solid #e0e0e0;
                }}
                
                .footer p {{
                    margin: 5px 0;
                }}
                
                .cta-button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: 600;
                    margin: 20px 0;
                    transition: background 0.3s ease;
                }}
                
                .cta-button:hover {{
                    background: #764ba2;
                }}
                
                @media (max-width: 600px) {{
                    .info-grid, .weather-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .content {{
                        padding: 20px;
                    }}
                    
                    .header {{
                        padding: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🌍 Relatório de UTCs</h1>
                    <p>Previsão de Tempo para Apresentação</p>
                </div>
                
                <div class="content">
                    <div class="greeting">
                        <p>Prezados,</p>
                        <p>Segue em anexo o relatório com informações sobre as zonas horárias mundiais e previsões de tempo para a apresentação no Jornal Local da Gazeta AL.</p>
                    </div>
        """
        
        # Adicionar cards das UTCs
        for utc in utcs_data:
            html += EmailSender._build_utc_card(utc)
        
        html += f"""
                    <div style="text-align: center; margin-top: 30px;">
                        <p><strong>Data do Relatório:</strong> {current_date}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Relatório Automático - Sistema de Gestão de UTCs</strong></p>
                    <p>Disciplina: Banco de Dados | Equipe de Desenvolvimento</p>
                    <p>Este é um email automático. Não responda diretamente.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def _build_utc_card(utc: Dict[str, Any]) -> str:
        """
        Constrói o card HTML para uma UTC no email
        
        Args:
            utc: Dados da UTC
        
        Returns:
            str: HTML do card
        """
        html = f"""
                    <div class="utc-card">
                        <h3>{utc.get('city_name', 'N/A')} 🌍</h3>
                        <p><strong>País:</strong> {utc.get('country', 'N/A')}</p>
                        <p><strong>Descrição:</strong> {utc.get('description', 'N/A')}</p>
                        
                        <div class="info-grid">
                            <div class="info-item">
                                <strong>Fuso Horário</strong>
                                <span>{utc.get('utc_offset', 'N/A')}</span>
                            </div>
                            <div class="info-item">
                                <strong>Zona UTC</strong>
                                <span>{utc.get('utc_name', 'N/A')}</span>
                            </div>
                        </div>
        """
        
        # Adicionar informações de clima se disponível
        if utc.get('temperature') or utc.get('weather_condition'):
            html += f"""
                        <div class="weather-info">
                            <h4>🌤️ Previsão de Tempo</h4>
                            <div class="weather-grid">
                                <div class="weather-item">
                                    <div>Condição</div>
                                    <div>{utc.get('weather_condition', 'N/A')}</div>
                                </div>
                                <div class="weather-item">
                                    <div>Temperatura</div>
                                    <div>{utc.get('temperature', 'N/A')}°C</div>
                                </div>
                                <div class="weather-item">
                                    <div>Umidade</div>
                                    <div>{utc.get('humidity', 'N/A')}%</div>
                                </div>
                                <div class="weather-item">
                                    <div>Vento</div>
                                    <div>{utc.get('wind_speed', 'N/A')} km/h</div>
                                </div>
            """
            
            if utc.get('climate_type'):
                html += f"""
                                <div class="weather-item">
                                    <div>Clima</div>
                                    <div>{utc.get('climate_type', 'N/A')}</div>
                                </div>
            """
            
            html += """
                            </div>
            """
            
            if utc.get('image_url') or utc.get('video_url'):
                html += """
                            <div class="media-links">
            """
                
                if utc.get('image_url'):
                    html += f"""
                                <a href="{utc.get('image_url')}" class="media-link" target="_blank">📸 Ver Imagem</a>
            """
                
                if utc.get('video_url'):
                    html += f"""
                                <a href="{utc.get('video_url')}" class="media-link" target="_blank">🎥 Ver Vídeo</a>
            """
                
                html += """
                            </div>
            """
            
            html += """
                        </div>
            """
        
        html += """
                    </div>
        """
        
        return html
