"""
Módulo de Geração de Relatórios HTML
Cria relatórios em HTML com informações de UTCs e previsão de tempo
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import logging
from config.config import TEMPLATES_DIR, REPORTS_DIR, LOGGING_CONFIG

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    filename=LOGGING_CONFIG['file']
)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Classe para gerar relatórios em HTML"""
    
    def __init__(self):
        """Inicializa o gerador de relatórios"""
        self.reports_dir = REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_daily_report(self, utcs_data: List[Dict[str, Any]]) -> str:
        """
        Gera um relatório diário com informações de UTCs
        
        Args:
            utcs_data: Lista com dados das UTCs e previsão de tempo
        
        Returns:
            str: Caminho do arquivo gerado
        """
        try:
            # Usar timestamp completo com data, hora e segundos para evitar sobrescrita
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"relatorio_utc_{timestamp}.html"
            filepath = os.path.join(self.reports_dir, filename)
            
            html_content = self._build_html_report(utcs_data, timestamp)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Relatório gerado com sucesso: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return None
    
    def _build_html_report(self, utcs_data: List[Dict], date: str) -> str:
        """
        Constrói o conteúdo HTML do relatório
        
        Args:
            utcs_data: Dados das UTCs
            date: Data do relatório
        
        Returns:
            str: HTML do relatório
        """
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de UTCs - {date}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    min-height: 100vh;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                
                .header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }}
                
                .header p {{
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                
                .date-info {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 15px;
                    display: inline-block;
                }}
                
                .content {{
                    padding: 40px;
                }}
                
                .utc-section {{
                    margin-bottom: 40px;
                    border-left: 5px solid #667eea;
                    padding-left: 25px;
                    transition: all 0.3s ease;
                }}
                
                .utc-section:hover {{
                    border-left-color: #764ba2;
                    padding-left: 30px;
                }}
                
                .utc-header {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                
                .utc-title {{
                    font-size: 1.8em;
                    color: #333;
                    font-weight: 600;
                }}
                
                .utc-badge {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin-left: 15px;
                    font-weight: 500;
                }}
                
                .utc-info {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 25px;
                }}
                
                .info-box {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                }}
                
                .info-label {{
                    color: #667eea;
                    font-weight: 600;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                
                .info-value {{
                    color: #333;
                    font-size: 1.1em;
                    font-weight: 500;
                }}
                
                .weather-section {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 25px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                
                .weather-header {{
                    font-size: 1.3em;
                    color: #333;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                
                .weather-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                }}
                
                .weather-item {{
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}
                
                .weather-icon {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                
                .weather-label {{
                    font-size: 0.85em;
                    color: #666;
                    margin-bottom: 5px;
                }}
                
                .weather-value {{
                    font-size: 1.3em;
                    color: #667eea;
                    font-weight: 600;
                }}
                
                .media-section {{
                    margin-top: 25px;
                }}
                
                .media-header {{
                    font-size: 1.1em;
                    color: #333;
                    font-weight: 600;
                    margin-bottom: 15px;
                }}
                
                .media-gallery {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 15px;
                }}
                
                .media-item {{
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    transition: transform 0.3s ease;
                }}
                
                .media-item:hover {{
                    transform: translateY(-5px);
                }}
                
                .media-item img {{
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                    display: block;
                }}
                
                .media-item video {{
                    width: 100%;
                    height: 200px;
                    display: block;
                }}
                
                .media-link {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-size: 0.9em;
                    margin-top: 10px;
                    transition: background 0.3s ease;
                }}
                
                .media-link:hover {{
                    background: #764ba2;
                }}
                
                .climate-badge {{
                    display: inline-block;
                    background: #e8f5e9;
                    color: #2e7d32;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: 500;
                    margin-top: 10px;
                }}
                
                .climate-arid {{ background: #fff3e0; color: #e65100; }}
                .climate-desert {{ background: #ffe0b2; color: #bf360c; }}
                .climate-tropical {{ background: #e0f2f1; color: #004d40; }}
                .climate-temperate {{ background: #f3e5f5; color: #6a1b9a; }}
                .climate-cold {{ background: #e3f2fd; color: #01579b; }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 25px;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #e0e0e0;
                }}
                
                .footer-info {{
                    font-size: 0.9em;
                    margin-bottom: 10px;
                }}
                
                .disclaimer {{
                    font-size: 0.85em;
                    color: #999;
                    margin-top: 15px;
                    font-style: italic;
                }}
                
                @media (max-width: 768px) {{
                    .header h1 {{
                        font-size: 1.8em;
                    }}
                    
                    .utc-info {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .media-gallery {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Relatório de UTCs - Previsão de Tempo</h1>
                    <p>Informações para apresentação no Jornal Local da Gazeta AL</p>
                    <div class="date-info">
                        <strong>Gerado em:</strong> {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
                    </div>
                </div>
                
                <div class="content">
        """
        
        # Adicionar dados de cada UTC
        for utc in utcs_data:
            html += self._build_utc_section(utc)
        
        html += """
                </div>
                
                <div class="footer">
                    <div class="footer-info">
                        <strong>Relatório Gerado Automaticamente</strong>
                    </div>
                    <div class="footer-info">
                        Equipe de Desenvolvimento | Disciplina: Banco de Dados
                    </div>
                    <div class="footer-info">
                        <strong>Dados de Clima:</strong> Fornecidos por WeatherAPI.com em tempo real
                    </div>
                    <div class="disclaimer">
                        Este relatório contém informações sobre zonas horárias mundiais e previsões de tempo REAIS.
                        Os dados climáticos são atualizados via API e refletem as condições meteorológicas atuais de cada região.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_utc_section(self, utc: Dict[str, Any]) -> str:
        """
        Constrói a seção HTML para uma UTC
        
        Args:
            utc: Dados da UTC
        
        Returns:
            str: HTML da seção
        """
        climate_class = self._get_climate_class(utc.get('climate_type', ''))
        weather_icon = self._get_weather_icon(utc.get('weather_condition', 'Nublado'))
        
        html = f"""
                    <div class="utc-section">
                        <div class="utc-header">
                            <h2 class="utc-title">{utc.get('city_name', 'N/A')} 🌍</h2>
                            <span class="utc-badge">{utc.get('utc_name', 'UTC')}</span>
                        </div>
                        
                        <div class="utc-info">
                            <div class="info-box">
                                <div class="info-label">País</div>
                                <div class="info-value">{utc.get('country', 'N/A')}</div>
                            </div>
                            <div class="info-box">
                                <div class="info-label">Fuso Horário</div>
                                <div class="info-value">{utc.get('utc_offset', 'N/A')}</div>
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Descrição</div>
                            <div class="info-value">{utc.get('description', 'N/A')}</div>
                        </div>
        """
        
        # Adicionar seção de clima/tempo se disponível
        if 'temperature' in utc or 'weather_condition' in utc:
            html += f"""
                        <div class="weather-section">
                            <div class="weather-header">🌤️ Previsão de Tempo</div>
                            <div class="weather-grid">
                                <div class="weather-item">
                                    <div class="weather-icon">{weather_icon}</div>
                                    <div class="weather-label">Condição</div>
                                    <div class="weather-value">{utc.get('weather_condition', 'N/A')}</div>
                                </div>
                                <div class="weather-item">
                                    <div class="weather-icon">🌡️</div>
                                    <div class="weather-label">Temperatura</div>
                                    <div class="weather-value">{utc.get('temperature', 'N/A')}°C</div>
                                </div>
                                <div class="weather-item">
                                    <div class="weather-icon">💧</div>
                                    <div class="weather-label">Umidade</div>
                                    <div class="weather-value">{utc.get('humidity', 'N/A')}%</div>
                                </div>
                                <div class="weather-item">
                                    <div class="weather-icon">💨</div>
                                    <div class="weather-label">Vento</div>
                                    <div class="weather-value">{utc.get('wind_speed', 'N/A')} km/h</div>
                                </div>
                            </div>
            """
            
            if utc.get('climate_type'):
                html += f"""
                            <div style="margin-top: 15px;">
                                <span class="climate-badge climate-{climate_class.lower()}">
                                    🌍 Clima: {utc.get('climate_type', 'N/A')}
                                </span>
                            </div>
            """
            
            html += """
                        </div>
            """
        
        # Adicionar seção de mídia
        if utc.get('image_url') or utc.get('video_url'):
            html += """
                        <div class="media-section">
                            <div class="media-header">📸 Mídia da Região</div>
                            <div class="media-gallery">
            """
            
            if utc.get('image_url'):
                html += f"""
                                <div class="media-item">
                                    <img src="{utc.get('image_url')}" alt="Imagem de {utc.get('city_name', 'UTC')}">
                                    <a href="{utc.get('image_url')}" class="media-link" target="_blank">Ver Imagem</a>
                                </div>
            """
            
            if utc.get('video_url'):
                html += f"""
                                <div class="media-item">
                                    <video controls>
                                        <source src="{utc.get('video_url')}" type="video/mp4">
                                        Seu navegador não suporta o elemento de vídeo.
                                    </video>
                                    <a href="{utc.get('video_url')}" class="media-link" target="_blank">Ver Vídeo</a>
                                </div>
            """
            
            html += """
                            </div>
                        </div>
            """
        
        html += """
                    </div>
        """
        
        return html
    
    @staticmethod
    def _get_weather_icon(condition: str) -> str:
        """
        Retorna um ícone emoji baseado na condição de tempo
        
        Args:
            condition: Condição de tempo
        
        Returns:
            str: Ícone emoji
        """
        condition_lower = condition.lower()
        
        icons = {
            'sol': '☀️',
            'ensolarado': '☀️',
            'sunny': '☀️',
            'chuva': '🌧️',
            'chuvoso': '🌧️',
            'rainy': '🌧️',
            'nuvem': '☁️',
            'nublado': '☁️',
            'cloudy': '☁️',
            'neve': '❄️',
            'snowy': '❄️',
            'tempestade': '⛈️',
            'tempestuoso': '⛈️',
            'storm': '⛈️',
            'seco': '🏜️',
            'arid': '🏜️',
            'árido': '🏜️',
            'deserto': '🏜️',
            'úmido': '💧',
            'humid': '💧',
            'tropical': '🌴',
            'vento': '💨',
            'windy': '💨',
            'nevoeiro': '🌫️',
            'foggy': '🌫️'
        }
        
        for key, icon in icons.items():
            if key in condition_lower:
                return icon
        
        return '🌤️'  # Ícone padrão
    
    @staticmethod
    def _get_climate_class(climate_type: str) -> str:
        """
        Retorna a classe CSS para o tipo de clima
        
        Args:
            climate_type: Tipo de clima
        
        Returns:
            str: Nome da classe CSS
        """
        climate_lower = climate_type.lower()
        
        if 'árido' in climate_lower or 'arid' in climate_lower:
            return 'arid'
        elif 'deserto' in climate_lower or 'desert' in climate_lower:
            return 'desert'
        elif 'tropical' in climate_lower:
            return 'tropical'
        elif 'temperado' in climate_lower or 'temperate' in climate_lower:
            return 'temperate'
        elif 'frio' in climate_lower or 'cold' in climate_lower:
            return 'cold'
        else:
            return 'temperate'
