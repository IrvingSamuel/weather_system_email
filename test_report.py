"""
Teste simples de geracao de relatorio
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import DatabaseConnection, UTCRepository, WeatherRepository
from src.report_generator import ReportGenerator
from src.weather_api import WeatherAPIClient, get_location_for_utc
from config.config import REPORTS_DIR, WEATHER_API_CONFIG, DB_CONFIG
import psycopg2
from datetime import date

def test_report_generation():
    """Testa geracao de relatorio com atualizacao automatica"""
    try:
        print("=" * 70)
        print("  GERACAO DE RELATORIO COM DADOS ATUAIS")
        print("=" * 70)
        
        # PASSO 1: Atualizar dados de clima da API
        print("\n[1/3] Atualizando dados de clima da API...")
        print("-" * 70)
        
        api_client = WeatherAPIClient(WEATHER_API_CONFIG['api_key'])
        
        db = DatabaseConnection()
        if not db.connect():
            print("ERRO - Falha ao conectar ao banco")
            return False
        
        # Buscar UTCs
        utc_repo = UTCRepository(db)
        utcs = utc_repo.get_all_utcs()
        
        if not utcs:
            print("ERRO - Nenhuma UTC encontrada")
            return False
        
        print(f"Encontradas {len(utcs)} UTCs")
        
        # Conectar diretamente para atualizar dados
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Limpar dados antigos
        cur.execute("DELETE FROM weather_predictions")
        conn.commit()
        
        print("\nBuscando clima ATUAL de cada UTC...")
        for utc in utcs:
            utc_name = utc.get('utc_name')
            city_name = utc.get('city_name')
            utc_id = utc.get('utc_id')
            
            # Buscar clima atual da API
            location = city_name if city_name else get_location_for_utc(utc_name)
            
            weather_data = api_client.get_current_weather(location)
            
            if weather_data:
                climate_type = api_client.determine_climate_type(
                    location,
                    weather_data['temperature'],
                    weather_data['humidity']
                )
                
                cur.execute("""
                    INSERT INTO weather_predictions 
                    (utc_id, forecast_date, temperature, weather_condition, 
                     humidity, wind_speed, climate_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    utc_id,
                    date.today(),
                    weather_data['temperature'],
                    weather_data['weather_condition'],  # Ja traduzido
                    weather_data['humidity'],
                    weather_data['wind_speed'],
                    climate_type
                ))
                
                conn.commit()
                print(f"  ✓ {utc_name:8} - {weather_data['temperature']:5.1f}°C - {weather_data['weather_condition']}")
        
        cur.close()
        conn.close()
        
        print("\nOK - Dados de clima atualizados da API")
        
        # PASSO 2: Buscar dados atualizados do banco
        print("\n[2/3] Buscando dados do banco...")
        print("-" * 70)
        weather_repo = WeatherRepository(db)
        report_data = []
        
        for utc in utcs:
            # Buscar ultimo dado de tempo
            latest = weather_repo.get_latest_weather(utc['utc_id'])
            
            if latest:
                report_data.append({
                    'utc_id': utc.get('utc_id'),
                    'city_name': utc.get('city_name'),
                    'country': utc.get('country'),
                    'utc_name': utc.get('utc_name'),
                    'utc_offset': utc.get('utc_offset'),
                    'description': utc.get('description'),
                    'temperature': latest.get('temperature'),
                    'weather_condition': latest.get('weather_condition'),
                    'humidity': latest.get('humidity'),
                    'wind_speed': latest.get('wind_speed'),
                    'climate_type': latest.get('climate_type'),
                    'image_url': utc.get('image_url'),
                    'video_url': utc.get('video_url')
                })
        
        print(f"OK - Dados de tempo para {len(report_data)} UTCs")
        
        # PASSO 3: Gerar relatorio
        print("\n[3/3] Gerando relatorio HTML...")
        print("-" * 70)
        
        generator = ReportGenerator()
        
        if not report_data:
            print("AVISO - Nenhum dado de tempo disponivel")
            db.disconnect()
            return False
        
        # Gerar relatorio (agora com timestamp completo)
        filepath = generator.generate_daily_report(report_data)
        
        if not filepath:
            print("ERRO - Nao conseguiu gerar relatorio HTML")
            db.disconnect()
            return False
        
        # Verificar se arquivo foi criado
        if not Path(filepath).exists():
            print(f"ERRO - Arquivo nao foi criado: {filepath}")
            db.disconnect()
            return False
        
        # Obter tamanho do arquivo
        file_size = Path(filepath).stat().st_size
        
        print("OK - Relatorio HTML gerado")
        print(f"OK - Relatorio salvo em: {filepath}")
        print(f"     Tamanho: {file_size} bytes")
        
        # Validar conteúdo
        if file_size < 1000:
            print(f"AVISO - Arquivo muito pequeno ({file_size} bytes). Pode estar vazio ou incompleto.")
        else:
            print(f"OK - Arquivo parece completo ({file_size} bytes)")
        
        db.disconnect()
        
        print("\n" + "=" * 70)
        print("  ✅ RELATORIO GERADO COM SUCESSO!")
        print("=" * 70)
        print(f"\nArquivo: {Path(filepath).name}")
        print(f"Pasta: {REPORTS_DIR}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"ERRO - {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if test_report_generation():
        sys.exit(0)
    else:
        print("\nERRO - Falha ao gerar relatorio")
        sys.exit(1)
