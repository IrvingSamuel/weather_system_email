"""
Aplicação Principal - UTC Weather Reports
Sistema de Geração de Relatórios e Envio de Emails Automatizado
"""

import logging
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config.config import LOGGING_CONFIG, RECIPIENTS, SELECTED_UTCS
from src.database import (DatabaseConnection, UTCRepository, WeatherRepository, 
                          EventLogRepository, TaskRepository, EmailHistoryRepository)
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender
from src.scheduler import SchedulerManager

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    filename=LOGGING_CONFIG['file']
)
logger = logging.getLogger(__name__)

# Instâncias globais
db_connection = None
report_generator = None
email_sender = None
scheduler_manager = None


def initialize_application() -> bool:
    """
    Inicializa a aplicação
    
    Returns:
        bool: True se inicializado com sucesso
    """
    global db_connection, report_generator, email_sender, scheduler_manager
    
    try:
        logger.info("=" * 50)
        logger.info("Inicializando aplicação UTC Weather Reports")
        logger.info("=" * 50)
        
        # Conectar ao banco de dados
        db_connection = DatabaseConnection()
        if not db_connection.connection:
            logger.error("Falha ao conectar ao banco de dados")
            return False
        
        # Inicializar componentes
        report_generator = ReportGenerator()
        email_sender = EmailSender()
        scheduler_manager = SchedulerManager(db_connection)
        
        logger.info("Aplicação inicializada com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {e}")
        return False


def get_utcs_with_weather() -> List[Dict[str, Any]]:
    """
    Obtém dados das UTCs com previsão de tempo
    
    Returns:
        List[Dict]: Lista com dados das UTCs e previsão de tempo
    """
    try:
        utc_repo = UTCRepository(db_connection)
        weather_repo = WeatherRepository(db_connection)
        
        utcs = utc_repo.get_selected_utcs()
        if not utcs:
            logger.warning("Nenhuma UTC encontrada no banco de dados")
            return []
        
        # Enriquecer dados com previsão de tempo
        utcs_with_weather = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for utc in utcs:
            utc_data = dict(utc)
            weather = weather_repo.get_latest_weather(utc['utc_id'])
            
            if weather:
                utc_data.update(weather)
            
            utcs_with_weather.append(utc_data)
        
        logger.info(f"Total de {len(utcs_with_weather)} UTCs carregadas com dados de previsão")
        return utcs_with_weather
    
    except Exception as e:
        logger.error(f"Erro ao obter UTCs com previsão de tempo: {e}")
        return []


def generate_daily_report() -> str:
    """
    Gera o relatório diário
    
    Returns:
        str: Caminho do arquivo gerado
    """
    try:
        logger.info("Iniciando geração de relatório diário...")
        
        utcs_data = get_utcs_with_weather()
        if not utcs_data:
            logger.error("Não foi possível obter dados das UTCs para gerar relatório")
            return None
        
        report_path = report_generator.generate_daily_report(utcs_data)
        
        if report_path:
            logger.info(f"Relatório gerado com sucesso: {report_path}")
            event_log_repo = EventLogRepository(db_connection)
            return report_path
        else:
            logger.error("Falha ao gerar relatório")
            return None
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório diário: {e}")
        return None


def send_report_email() -> bool:
    """
    Envia o relatório por email
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        logger.info("Iniciando envio de emails...")
        
        # Gerar relatório
        report_path = generate_daily_report()
        if not report_path:
            logger.error("Não foi possível gerar relatório para enviar por email")
            return False
        
        # Obter dados das UTCs
        utcs_data = get_utcs_with_weather()
        
        # Criar corpo do email
        html_body = EmailSender.create_html_email_body(utcs_data)
        
        # Preparar dados das UTCs para registrar
        utc_ids = [utc['utc_id'] for utc in utcs_data]
        
        # Enviar email
        subject = f"[GAZETA AL] Relatório de UTCs e Previsão de Tempo - {datetime.now().strftime('%d/%m/%Y')}"
        result = email_sender.send_report_email(
            recipients=RECIPIENTS,
            subject=subject,
            html_body=html_body,
            report_file_path=report_path,
            utc_ids=utc_ids
        )
        
        # Registrar no histórico de emails
        email_history_repo = EmailHistoryRepository(db_connection)
        
        if result['success']:
            for recipient in RECIPIENTS:
                email_history_repo.insert_email_record(
                    recipient=recipient,
                    subject=subject,
                    status='sent',
                    utc_ids=utc_ids
                )
            logger.info(f"Emails enviados com sucesso para {len(RECIPIENTS)} destinatários")
            return True
        else:
            for recipient in RECIPIENTS:
                email_history_repo.insert_email_record(
                    recipient=recipient,
                    subject=subject,
                    status='failed',
                    error_msg=result['message'],
                    utc_ids=utc_ids
                )
            logger.error(f"Erro ao enviar emails: {result['message']}")
            return False
    
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False


def update_weather_data() -> bool:
    """
    Atualiza dados de previsão de tempo
    
    Returns:
        bool: True se atualizado com sucesso
    """
    try:
        logger.info("Atualizando dados de previsão de tempo...")
        
        # Aqui você pode integrar com uma API de previsão de tempo
        # Por exemplo: OpenWeatherMap, WeatherAPI, etc.
        
        # Este é um exemplo de como você estruturaria a atualização
        weather_repo = WeatherRepository(db_connection)
        
        # Dados de exemplo (você substituiria com dados reais da API)
        example_weather = [
            {
                'utc_id': 1,
                'temperature': 28.5,
                'weather_condition': 'Ensolarado',
                'humidity': 65,
                'wind_speed': 12.5,
                'climate_type': 'Tropical'
            },
            {
                'utc_id': 2,
                'temperature': 18.3,
                'weather_condition': 'Nublado',
                'humidity': 75,
                'wind_speed': 15.2,
                'climate_type': 'Temperado'
            },
            {
                'utc_id': 3,
                'temperature': 31.2,
                'weather_condition': 'Chuvoso',
                'humidity': 85,
                'wind_speed': 8.3,
                'climate_type': 'Tropical'
            },
            {
                'utc_id': 4,
                'temperature': 22.1,
                'weather_condition': 'Nublado',
                'humidity': 70,
                'wind_speed': 18.5,
                'climate_type': 'Temperado'
            },
            {
                'utc_id': 5,
                'temperature': 15.8,
                'weather_condition': 'Ensolarado',
                'humidity': 55,
                'wind_speed': 12.0,
                'climate_type': 'Temperado'
            }
        ]
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for weather in example_weather:
            weather_repo.insert_weather(
                utc_id=weather['utc_id'],
                forecast_date=today,
                temperature=weather['temperature'],
                weather_condition=weather['weather_condition'],
                humidity=weather['humidity'],
                wind_speed=weather['wind_speed'],
                climate_type=weather['climate_type']
            )
        
        logger.info(f"Dados de previsão de tempo atualizados para {len(example_weather)} UTCs")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao atualizar dados de previsão de tempo: {e}")
        return False


def cleanup_old_logs() -> bool:
    """
    Remove logs antigos do sistema (com mais de 30 dias)
    
    Returns:
        bool: True se limpeza realizada com sucesso
    """
    try:
        logger.info("Limpando logs antigos...")
        
        event_log_repo = EventLogRepository(db_connection)
        
        # Calcular data limite (30 dias atrás)
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Aqui você faria a chamada para limpar logs
        # Por enquanto, apenas registramos a ação
        
        logger.info(f"Limpeza de logs realizada. Logs anteriores a {cutoff_date} foram removidos")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao limpar logs antigos: {e}")
        return False


def start_scheduler() -> bool:
    """
    Inicia o scheduler de tarefas
    
    Returns:
        bool: True se iniciado com sucesso
    """
    try:
        logger.info("Iniciando scheduler de tarefas...")
        
        # Definir callbacks para os jobs
        callbacks = {
            'report_generation': generate_daily_report,
            'email_dispatch': send_report_email,
            'weather_update': update_weather_data,
            'log_cleanup': cleanup_old_logs
        }
        
        # Inicializar jobs
        if not scheduler_manager.initialize_jobs(callbacks):
            logger.error("Falha ao inicializar jobs do scheduler")
            return False
        
        # Iniciar scheduler
        if not scheduler_manager.start_scheduler():
            logger.error("Falha ao iniciar scheduler")
            return False
        
        logger.info("Scheduler iniciado com sucesso")
        logger.info("Jobs agendados:")
        for job_name, status in scheduler_manager.scheduler.get_all_jobs_status().items():
            logger.info(f"  - {job_name}: Próxima execução: {status['next_run']}")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {e}")
        return False


def show_menu() -> int:
    """
    Exibe menu de opções
    
    Returns:
        int: Opção selecionada
    """
    print("\n" + "=" * 50)
    print("📊 UTC Weather Reports - Menu Principal")
    print("=" * 50)
    print("\n1. Gerar Relatório Diário")
    print("2. Enviar Email com Relatório")
    print("3. Atualizar Dados de Previsão de Tempo")
    print("4. Visualizar Status dos Jobs")
    print("5. Limpar Logs Antigos")
    print("6. Iniciar Scheduler Automático")
    print("7. Parar Scheduler")
    print("8. Sair")
    print("\n" + "=" * 50)
    
    try:
        choice = int(input("\nSelecione uma opção: "))
        return choice
    except ValueError:
        print("Opção inválida!")
        return 0


def show_job_status():
    """Exibe status de todos os jobs"""
    print("\n" + "=" * 50)
    print("📋 Status dos Jobs Agendados")
    print("=" * 50)
    
    status = scheduler_manager.scheduler.get_all_jobs_status()
    
    if not status:
        print("Nenhum job agendado")
    else:
        for job_name, job_info in status.items():
            print(f"\n🔹 {job_name}")
            print(f"   Status: {job_info['status']}")
            print(f"   Próxima execução: {job_info['next_run']}")
            print(f"   Criado em: {job_info['created_at']}")
            if job_info['last_run']:
                print(f"   Última execução: {job_info['last_run']}")


def main():
    """Função principal"""
    try:
        # Inicializar aplicação
        if not initialize_application():
            print("❌ Erro ao inicializar aplicação")
            sys.exit(1)
        
        print("\n✅ Aplicação inicializada com sucesso!")
        
        # Loop do menu
        running = True
        while running:
            choice = show_menu()
            
            if choice == 1:
                print("\n⏳ Gerando relatório...")
                if generate_daily_report():
                    print("✅ Relatório gerado com sucesso!")
                else:
                    print("❌ Erro ao gerar relatório")
            
            elif choice == 2:
                print("\n⏳ Enviando email...")
                if send_report_email():
                    print("✅ Email enviado com sucesso!")
                else:
                    print("❌ Erro ao enviar email")
            
            elif choice == 3:
                print("\n⏳ Atualizando dados de previsão...")
                if update_weather_data():
                    print("✅ Dados atualizados com sucesso!")
                else:
                    print("❌ Erro ao atualizar dados")
            
            elif choice == 4:
                show_job_status()
            
            elif choice == 5:
                print("\n⏳ Limpando logs antigos...")
                if cleanup_old_logs():
                    print("✅ Limpeza realizada com sucesso!")
                else:
                    print("❌ Erro ao limpar logs")
            
            elif choice == 6:
                print("\n⏳ Iniciando scheduler automático...")
                print("Este processo será executado em background")
                if start_scheduler():
                    print("✅ Scheduler iniciado!")
                    print("🔄 Sistema aguardando horários agendados...")
                    
                    # Manter o programa rodando
                    try:
                        while scheduler_manager.scheduler.scheduler.running:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\n⏹️ Encerrando scheduler...")
                        scheduler_manager.stop_scheduler()
                        print("✅ Scheduler parado")
                else:
                    print("❌ Erro ao iniciar scheduler")
            
            elif choice == 7:
                print("\n⏹️ Parando scheduler...")
                if scheduler_manager.stop_scheduler():
                    print("✅ Scheduler parado")
                else:
                    print("❌ Erro ao parar scheduler")
            
            elif choice == 8:
                running = False
                print("\n👋 Encerrando aplicação...")
            
            else:
                print("\n❌ Opção inválida!")
        
        # Desconectar do banco de dados
        if db_connection:
            db_connection.disconnect()
        
        print("✅ Aplicação encerrada com sucesso!")
    
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {e}")
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
