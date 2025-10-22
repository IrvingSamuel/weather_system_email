"""
Script para atualizar dados de clima usando WeatherAPI.com
Busca dados reais e atualiza o banco de dados
"""

import sys
from pathlib import Path
from datetime import datetime, date
import psycopg2

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.weather_api import WeatherAPIClient, get_location_for_utc
from src.database import DatabaseConnection, UTCRepository, WeatherRepository
from config.config import WEATHER_API_CONFIG, DB_CONFIG

def update_weather_data():
    """Atualiza dados de clima no banco usando API real"""
    
    print("=" * 80)
    print("  ATUALIZACAO DE DADOS DE CLIMA - WEATHERAPI.COM")
    print("=" * 80)
    
    # Inicializar cliente da API
    print(f"\n1. Inicializando cliente WeatherAPI...")
    api_client = WeatherAPIClient(WEATHER_API_CONFIG['api_key'])
    print("   OK - Cliente inicializado")
    
    # Conectar ao banco
    print("\n2. Conectando ao banco de dados...")
    db = DatabaseConnection()
    if not db.connect():
        print("   ERRO - Falha ao conectar")
        return False
    print("   OK - Conectado")
    
    # Buscar UTCs
    print("\n3. Buscando UTCs cadastradas...")
    utc_repo = UTCRepository(db)
    utcs = utc_repo.get_all_utcs()
    
    if not utcs:
        print("   ERRO - Nenhuma UTC encontrada")
        return False
    
    print(f"   OK - {len(utcs)} UTCs encontradas")
    
    # Atualizar clima para cada UTC
    print("\n4. Buscando dados de clima da API...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Limpar previsões antigas
        print("   - Limpando previsões antigas...")
        cur.execute("DELETE FROM weather_predictions")
        conn.commit()
        
        success_count = 0
        
        for utc in utcs:
            utc_name = utc.get('utc_name')
            city_name = utc.get('city_name')
            utc_id = utc.get('utc_id')
            
            # Determinar localização para buscar
            location = city_name if city_name else get_location_for_utc(utc_name)
            
            print(f"\n   [{utc_name:8}] Buscando clima para: {location}")
            
            # Buscar dados atuais
            weather_data = api_client.get_current_weather(location)
            
            if weather_data:
                # Determinar tipo de clima
                climate_type = api_client.determine_climate_type(
                    location,
                    weather_data['temperature'],
                    weather_data['humidity']
                )
                
                # Inserir no banco
                today = date.today()
                
                try:
                    cur.execute("""
                        INSERT INTO weather_predictions 
                        (utc_id, forecast_date, temperature, weather_condition, 
                         humidity, wind_speed, climate_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        utc_id,
                        today,
                        weather_data['temperature'],
                        weather_data['weather_condition'],
                        weather_data['humidity'],
                        weather_data['wind_speed'],
                        climate_type
                    ))
                    
                    conn.commit()
                    
                    print(f"      ✓ Temperatura: {weather_data['temperature']}°C")
                    print(f"      ✓ Condição: {weather_data['weather_condition']}")
                    print(f"      ✓ Umidade: {weather_data['humidity']}%")
                    print(f"      ✓ Vento: {weather_data['wind_speed']} km/h")
                    print(f"      ✓ Clima: {climate_type}")
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"      ✗ Erro ao inserir no banco: {e}")
                    conn.rollback()
            else:
                print(f"      ✗ Falha ao buscar dados da API")
        
        cur.close()
        conn.close()
        db.disconnect()
        
        print("\n" + "=" * 80)
        print(f"  ✅ ATUALIZACAO CONCLUIDA!")
        print("=" * 80)
        print(f"\n  UTCs processadas: {len(utcs)}")
        print(f"  Sucessos: {success_count}")
        print(f"  Falhas: {len(utcs) - success_count}")
        print("\n" + "=" * 80)
        
        return success_count > 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if update_weather_data():
        print("\n✅ Dados de clima atualizados com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Falha ao atualizar dados de clima")
        sys.exit(1)
