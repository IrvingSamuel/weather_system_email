"""
Verificar dados completos das UTCs no banco
"""
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, UTCRepository, WeatherRepository

def verify_utc_data():
    """Verificar dados das UTCs"""
    print("=" * 70)
    print("  VERIFICACAO DE DADOS DAS UTCs")
    print("=" * 70)
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("ERRO - Nao conseguiu conectar ao banco")
        return False
    
    # Buscar UTCs
    utc_repo = UTCRepository(db)
    utcs = utc_repo.get_all_utcs()
    
    print(f"\n{len(utcs)} UTCs encontradas:\n")
    
    for i, utc in enumerate(utcs, 1):
        print(f"UTC {i}: {utc.get('city_name', 'N/A')}")
        print(f"  - ID: {utc.get('utc_id')}")
        print(f"  - Nome UTC: {utc.get('utc_name', 'N/A')}")
        print(f"  - Offset: {utc.get('utc_offset', 'N/A')}")
        print(f"  - Cidade: {utc.get('city_name', 'N/A')}")
        print(f"  - Pais: {utc.get('country', 'N/A')}")
        print(f"  - Descricao: {utc.get('description', 'N/A')}")
        print(f"  - Imagem: {utc.get('image_url', 'N/A')}")
        print(f"  - Video: {utc.get('video_url', 'N/A')}")
        
        # Buscar dados de clima
        weather_repo = WeatherRepository(db)
        latest = weather_repo.get_latest_weather(utc.get('utc_id'))
        
        if latest:
            print(f"  - Clima:")
            print(f"    * Temperatura: {latest.get('temperature')}°C")
            print(f"    * Condicao: {latest.get('weather_condition')}")
            print(f"    * Umidade: {latest.get('humidity')}%")
            print(f"    * Vento: {latest.get('wind_speed')} km/h")
            print(f"    * Tipo clima: {latest.get('climate_type')}")
        else:
            print(f"  - Clima: SEM DADOS")
        
        print()
    
    db.disconnect()
    return True

if __name__ == '__main__':
    verify_utc_data()
