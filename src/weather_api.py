"""
Weather API Integration - Busca dados reais de clima
API: weatherapi.com
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """Cliente para buscar dados de clima da WeatherAPI.com"""
    
    # Dicionário de tradução de condições climáticas
    WEATHER_TRANSLATIONS = {
        # Condições claras
        'sunny': 'Ensolarado',
        'clear': 'Limpo',
        'partly cloudy': 'Parcialmente Nublado',
        'cloudy': 'Nublado',
        'overcast': 'Encoberto',
        
        # Neblina/Névoa
        'mist': 'Névoa',
        'fog': 'Nevoeiro',
        'freezing fog': 'Nevoeiro Congelante',
        
        # Chuva
        'patchy rain possible': 'Possibilidade de Chuva',
        'patchy rain nearby': 'Chuva Próxima',
        'light rain': 'Chuva Leve',
        'moderate rain': 'Chuva Moderada',
        'moderate rain at times': 'Chuva Moderada Intermitente',
        'heavy rain': 'Chuva Forte',
        'heavy rain at times': 'Chuva Forte Intermitente',
        'light drizzle': 'Chuvisco Leve',
        'patchy light drizzle': 'Chuvisco Leve Intermitente',
        'light freezing rain': 'Chuva Congelante Leve',
        'moderate or heavy freezing rain': 'Chuva Congelante Moderada a Forte',
        'light rain shower': 'Pancadas de Chuva Leve',
        'moderate or heavy rain shower': 'Pancadas de Chuva Moderada a Forte',
        'torrential rain shower': 'Pancadas de Chuva Torrencial',
        
        # Neve
        'patchy snow possible': 'Possibilidade de Neve',
        'patchy light snow': 'Neve Leve Intermitente',
        'light snow': 'Neve Leve',
        'moderate snow': 'Neve Moderada',
        'heavy snow': 'Neve Forte',
        'patchy moderate snow': 'Neve Moderada Intermitente',
        'patchy heavy snow': 'Neve Forte Intermitente',
        'light snow showers': 'Pancadas de Neve Leve',
        'moderate or heavy snow showers': 'Pancadas de Neve Moderada a Forte',
        'blowing snow': 'Nevasca',
        'blizzard': 'Nevasca Intensa',
        
        # Gelo
        'ice pellets': 'Granizo',
        'light showers of ice pellets': 'Pancadas Leves de Granizo',
        'moderate or heavy showers of ice pellets': 'Pancadas Moderadas a Fortes de Granizo',
        
        # Trovoada
        'thundery outbreaks possible': 'Possibilidade de Trovoadas',
        'patchy light rain with thunder': 'Chuva Leve com Trovoadas Intermitente',
        'moderate or heavy rain with thunder': 'Chuva Moderada a Forte com Trovoadas',
        'patchy light snow with thunder': 'Neve Leve com Trovoadas Intermitente',
        'moderate or heavy snow with thunder': 'Neve Moderada a Forte com Trovoadas',
    }
    
    def __init__(self, api_key: str):
        """
        Inicializa o cliente da WeatherAPI
        
        Args:
            api_key: Chave da API do weatherapi.com
        """
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
    
    def translate_condition(self, condition: str) -> str:
        """
        Traduz a condição climática do inglês para português
        
        Args:
            condition: Condição em inglês
        
        Returns:
            Condição em português
        """
        condition_lower = condition.lower().strip()
        
        # Tentar tradução direta
        if condition_lower in self.WEATHER_TRANSLATIONS:
            return self.WEATHER_TRANSLATIONS[condition_lower]
        
        # Tentar tradução parcial (busca por palavras-chave)
        for key, value in self.WEATHER_TRANSLATIONS.items():
            if key in condition_lower:
                return value
        
        # Se não encontrar tradução, retornar original
        return condition
    
    def get_current_weather(self, location: str) -> Optional[Dict]:
        """
        Busca clima atual para uma localização
        
        Args:
            location: Nome da cidade ou coordenadas (lat,lon)
        
        Returns:
            Dict com dados de clima ou None se falhar
        """
        try:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': location,
                'aqi': 'no'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Traduzir condição climática
            original_condition = data['current']['condition']['text']
            translated_condition = self.translate_condition(original_condition)
            
            # Extrair dados relevantes
            weather_data = {
                'temperature': data['current']['temp_c'],
                'weather_condition': translated_condition,
                'weather_condition_en': original_condition,  # Manter original para referência
                'humidity': data['current']['humidity'],
                'wind_speed': data['current']['wind_kph'],
                'feels_like': data['current']['feelslike_c'],
                'pressure': data['current']['pressure_mb'],
                'visibility': data['current']['vis_km'],
                'uv_index': data['current']['uv'],
                'location_name': data['location']['name'],
                'country': data['location']['country'],
                'last_updated': data['current']['last_updated'],
                'is_day': data['current']['is_day'] == 1
            }
            
            logger.info(f"Clima obtido para {location}: {weather_data['temperature']}°C, {weather_data['weather_condition']}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar clima para {location}: {e}")
            return None
        except KeyError as e:
            logger.error(f"Erro ao processar resposta da API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None
    
    def get_forecast(self, location: str, days: int = 3) -> Optional[Dict]:
        """
        Busca previsão de clima para os próximos dias
        
        Args:
            location: Nome da cidade ou coordenadas
            days: Número de dias de previsão (1-10)
        
        Returns:
            Dict com dados de previsão ou None se falhar
        """
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': location,
                'days': min(days, 10),  # Máximo 10 dias
                'aqi': 'no',
                'alerts': 'no'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extrair previsão
            forecast_data = {
                'location': data['location']['name'],
                'country': data['location']['country'],
                'current': {
                    'temperature': data['current']['temp_c'],
                    'condition': data['current']['condition']['text'],
                    'humidity': data['current']['humidity'],
                    'wind_speed': data['current']['wind_kph']
                },
                'forecast_days': []
            }
            
            for day in data['forecast']['forecastday']:
                forecast_data['forecast_days'].append({
                    'date': day['date'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'avg_temp': day['day']['avgtemp_c'],
                    'condition': day['day']['condition']['text'],
                    'humidity': day['day']['avghumidity'],
                    'wind_speed': day['day']['maxwind_kph'],
                    'chance_of_rain': day['day'].get('daily_chance_of_rain', 0)
                })
            
            logger.info(f"Previsão obtida para {location}: {len(forecast_data['forecast_days'])} dias")
            return forecast_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar previsão para {location}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None
    
    def determine_climate_type(self, location: str, temp: float, humidity: int) -> str:
        """
        Determina o tipo de clima baseado em temperatura e umidade
        
        Args:
            location: Nome da localização
            temp: Temperatura em Celsius
            humidity: Umidade em %
        
        Returns:
            Tipo de clima
        """
        # Regiões conhecidas
        location_lower = location.lower()
        
        # Climas específicos por região
        if 'desert' in location_lower or 'sahara' in location_lower:
            return 'Desértico'
        elif 'arctic' in location_lower or 'antarctica' in location_lower:
            return 'Polar'
        
        # Baseado em temperatura e umidade
        if temp < 0:
            return 'Polar'
        elif temp < 10:
            if humidity > 70:
                return 'Temperado Úmido'
            else:
                return 'Temperado Seco'
        elif temp < 20:
            if humidity > 70:
                return 'Subtropical Úmido'
            else:
                return 'Subtropical'
        elif temp < 25:
            if humidity > 80:
                return 'Tropical Úmido'
            elif humidity < 40:
                return 'Árido'
            else:
                return 'Tropical de Altitude'
        else:  # temp >= 25
            if humidity > 70:
                return 'Tropical Úmido'
            elif humidity < 40:
                return 'Árido Tropical'
            else:
                return 'Tropical'

def get_location_for_utc(utc_name: str, city_name: str = None) -> str:
    """
    Retorna a localização apropriada para buscar clima baseado na UTC
    
    Args:
        utc_name: Nome da UTC (ex: UTC-12)
        city_name: Nome da cidade (opcional)
    
    Returns:
        String de localização para a API
    """
    if city_name:
        return city_name
    
    # Mapeamento de UTCs para cidades representativas
    utc_locations = {
        'UTC-12': 'Baker Island',
        'UTC-11': 'Pago Pago',
        'UTC-10': 'Honolulu',
        'UTC-9': 'Anchorage',
        'UTC-8': 'Los Angeles',
        'UTC-7': 'Denver',
        'UTC-6': 'Chicago',
        'UTC-5': 'Bogota',
        'UTC-4': 'New York',
        'UTC-3': 'Buenos Aires',
        'UTC-2': 'South Georgia',
        'UTC-1': 'Cape Verde',
        'UTC+0': 'London',
        'UTC+1': 'Paris',
        'UTC+2': 'Cairo',
        'UTC+3': 'Moscow',
        'UTC+4': 'Dubai',
        'UTC+5': 'Karachi',
        'UTC+6': 'Dhaka',
        'UTC+7': 'Bangkok',
        'UTC+8': 'Singapore',
        'UTC+9': 'Tokyo',
        'UTC+10': 'Sydney',
        'UTC+11': 'Honiara',
        'UTC+12': 'Auckland'
    }
    
    return utc_locations.get(utc_name, 'London')
