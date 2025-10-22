"""
Script para popular banco com UTCs corretas e dados realistas de clima
UTCs necessárias: UTC-12, UTC-11, UTC-5, UTC-1, UTC+11
"""

import psycopg2
from datetime import datetime, timedelta
from config.config import DB_CONFIG

def reset_and_populate_correct_data():
    """Reseta e popula com dados corretos"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("=" * 80)
        print("  RESET E POPULACAO COM DADOS CORRETOS")
        print("=" * 80)
        
        # PASSO 1: Limpar dados existentes
        print("\n1. Limpando dados existentes...")
        cur.execute("DELETE FROM weather_predictions")
        cur.execute("DELETE FROM email_history")
        cur.execute("DELETE FROM event_logs")
        cur.execute("DELETE FROM utcs")
        conn.commit()
        print("   OK - Dados antigos removidos")
        
        # PASSO 2: Inserir UTCs corretas
        print("\n2. Inserindo UTCs corretas...")
        
        utcs_data = [
            {
                'utc_name': 'UTC-12',
                'utc_offset': '-12:00',
                'city_name': 'Baker Island',
                'country': 'Estados Unidos',
                'latitude': 0.1936,
                'longitude': -176.4769,
                'description': 'Ilha Baker - Território dos EUA no Pacífico',
                'climate': 'Tropical',
                'temp_base': 28.0
            },
            {
                'utc_name': 'UTC-11',
                'utc_offset': '-11:00',
                'city_name': 'Pago Pago',
                'country': 'Samoa Americana',
                'latitude': -14.2756,
                'longitude': -170.7025,
                'description': 'Capital da Samoa Americana - Oceania',
                'climate': 'Tropical Úmido',
                'temp_base': 27.5
            },
            {
                'utc_name': 'UTC-5',
                'utc_offset': '-05:00',
                'city_name': 'Bogotá',
                'country': 'Colômbia',
                'latitude': 4.7110,
                'longitude': -74.0721,
                'description': 'Capital da Colômbia - Região Andina',
                'climate': 'Tropical de Altitude',
                'temp_base': 14.0
            },
            {
                'utc_name': 'UTC-1',
                'utc_offset': '-01:00',
                'city_name': 'Cabo Verde',
                'country': 'Cabo Verde',
                'latitude': 16.0000,
                'longitude': -24.0000,
                'description': 'Arquipélago de Cabo Verde - África Ocidental',
                'climate': 'Árido Tropical',
                'temp_base': 24.0
            },
            {
                'utc_name': 'UTC+11',
                'utc_offset': '+11:00',
                'city_name': 'Honiara',
                'country': 'Ilhas Salomão',
                'latitude': -9.4456,
                'longitude': 159.9729,
                'description': 'Capital das Ilhas Salomão - Oceania',
                'climate': 'Tropical Úmido',
                'temp_base': 26.5
            }
        ]
        
        utc_ids = {}
        for utc in utcs_data:
            cur.execute("""
                INSERT INTO utcs (utc_name, utc_offset, city_name, country, latitude, longitude, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING utc_id
            """, (
                utc['utc_name'],
                utc['utc_offset'],
                utc['city_name'],
                utc['country'],
                utc['latitude'],
                utc['longitude'],
                utc['description']
            ))
            utc_id = cur.fetchone()[0]
            utc_ids[utc['utc_name']] = {
                'id': utc_id,
                'climate': utc['climate'],
                'temp_base': utc['temp_base'],
                'city': utc['city_name']
            }
            print(f"   ✓ {utc['utc_name']:8} - {utc['city_name']:20} ({utc['country']})")
        
        conn.commit()
        print(f"   OK - {len(utcs_data)} UTCs inseridas")
        
        # PASSO 3: Inserir dados de clima REALISTAS e VARIADOS
        print("\n3. Inserindo dados de clima realistas...")
        
        # Dados específicos para cada UTC
        weather_scenarios = {
            'UTC-12': {  # Baker Island - Tropical quente
                'conditions': ['Ensolarado', 'Parcialmente Nublado', 'Nublado', 'Chuvoso'],
                'temp_range': (26, 31),
                'humidity_range': (70, 85),
                'wind_range': (15, 30),
                'climate': 'Tropical'
            },
            'UTC-11': {  # Pago Pago - Tropical úmido
                'conditions': ['Chuvoso', 'Nublado', 'Parcialmente Nublado', 'Ensolarado'],
                'temp_range': (24, 30),
                'humidity_range': (75, 90),
                'wind_range': (10, 25),
                'climate': 'Tropical Úmido'
            },
            'UTC-5': {  # Bogotá - Frio de altitude
                'conditions': ['Nublado', 'Chuvoso', 'Parcialmente Nublado', 'Ensolarado'],
                'temp_range': (8, 18),
                'humidity_range': (60, 80),
                'wind_range': (5, 15),
                'climate': 'Tropical de Altitude'
            },
            'UTC-1': {  # Cabo Verde - Árido
                'conditions': ['Ensolarado', 'Ensolarado', 'Parcialmente Nublado', 'Seco'],
                'temp_range': (22, 28),
                'humidity_range': (45, 65),
                'wind_range': (20, 35),
                'climate': 'Árido Tropical'
            },
            'UTC+11': {  # Honiara - Tropical quente úmido
                'conditions': ['Chuvoso', 'Nublado', 'Parcialmente Nublado', 'Ensolarado'],
                'temp_range': (24, 31),
                'humidity_range': (70, 90),
                'wind_range': (8, 20),
                'climate': 'Tropical Úmido'
            }
        }
        
        today = datetime.now().date()
        import random
        
        for utc_name, data in utc_ids.items():
            scenario = weather_scenarios[utc_name]
            
            for day_offset in range(7):  # 7 dias de previsão
                forecast_date = today + timedelta(days=day_offset)
                
                # Variar temperatura ao longo dos dias
                temp_min, temp_max = scenario['temp_range']
                temperature = round(random.uniform(temp_min, temp_max), 1)
                
                # Condição aleatória baseada no clima local
                condition = random.choice(scenario['conditions'])
                
                # Umidade variável
                hum_min, hum_max = scenario['humidity_range']
                humidity = random.randint(hum_min, hum_max)
                
                # Vento variável
                wind_min, wind_max = scenario['wind_range']
                wind_speed = round(random.uniform(wind_min, wind_max), 1)
                
                cur.execute("""
                    INSERT INTO weather_predictions 
                    (utc_id, forecast_date, temperature, weather_condition, humidity, wind_speed, climate_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['id'],
                    forecast_date,
                    temperature,
                    condition,
                    humidity,
                    wind_speed,
                    scenario['climate']
                ))
            
            print(f"   ✓ {utc_name:8} - {data['city']:20} - 7 previsões inseridas")
        
        conn.commit()
        print(f"   OK - {len(utc_ids) * 7} previsões inseridas")
        
        # PASSO 4: Verificação final
        print("\n4. Verificação final...")
        cur.execute("SELECT COUNT(*) FROM utcs")
        utc_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM weather_predictions")
        weather_count = cur.fetchone()[0]
        
        print(f"   ✓ UTCs no banco: {utc_count}")
        print(f"   ✓ Previsões no banco: {weather_count}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("  ✅ BANCO POPULADO COM SUCESSO!")
        print("=" * 80)
        print("\nUTCs configuradas:")
        print("  • UTC-12: Baker Island (Tropical)")
        print("  • UTC-11: Pago Pago (Tropical Úmido)")
        print("  • UTC-5:  Bogotá (Tropical de Altitude - Frio)")
        print("  • UTC-1:  Cabo Verde (Árido)")
        print("  • UTC+11: Honiara (Tropical Úmido)")
        print("\nCada UTC tem dados de clima ÚNICOS e REALISTAS!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    reset_and_populate_correct_data()
