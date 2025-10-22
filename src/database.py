"""
Módulo de Conexão com Banco de Dados PostgreSQL
Gerencia conexões PostgreSQL e operações de banco de dados
"""

import psycopg2
from psycopg2 import Error
import logging
from config.config import DB_CONFIG, LOGGING_CONFIG
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    filename=LOGGING_CONFIG['file']
)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Classe para gerenciar conexões com banco de dados PostgreSQL"""
    
    def __init__(self):
        """Inicializa a conexão com banco de dados"""
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Estabelece conexão com banco de dados PostgreSQL
        
        Returns:
            bool: True se conectado com sucesso, False caso contrário
        """
        try:
            self.connection = psycopg2.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port']
            )
            self.cursor = self.connection.cursor()
            # Usar RealDictCursor para resultados como dicts
            from psycopg2.extras import RealDictCursor
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            logger.info("Conexão com banco de dados PostgreSQL estabelecida com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao conectar ao banco de dados PostgreSQL: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Fecha a conexão com banco de dados
        
        Returns:
            bool: True se desconectado com sucesso
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Conexão com banco de dados fechada")
            return True
        except Error as e:
            logger.error(f"Erro ao desconectar do banco de dados: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Executa uma query de modificação (INSERT, UPDATE, DELETE)
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query
        
        Returns:
            bool: True se executado com sucesso
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            logger.info(f"Query executada com sucesso: {query[:50]}...")
            return True
        except Error as e:
            logger.error(f"Erro ao executar query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """
        Executa uma query de consulta (SELECT)
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query
        
        Returns:
            List[Dict]: Lista com resultados ou None em caso de erro
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            return results
        except Error as e:
            logger.error(f"Erro ao buscar dados: {e}")
            return None
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Executa uma query e retorna apenas um resultado
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query
        
        Returns:
            Dict: Um resultado ou None
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Erro ao buscar um dado: {e}")
            return None
    
    def close(self):
        """Fecha a conexão"""
        self.disconnect()


class UTCRepository:
    """Repositório para operações relacionadas a UTCs"""
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db: Instância de DatabaseConnection
        """
        self.db = db
    
    def get_all_utcs(self) -> Optional[List[Dict]]:
        """Retorna todas as UTCs cadastradas"""
        query = """
            SELECT utc_id, utc_name, utc_offset, city_name, country, 
                   latitude, longitude, description, created_at 
            FROM utcs 
            ORDER BY utc_name
        """
        return self.db.fetch_query(query)
    
    def get_utc_by_id(self, utc_id: int) -> Optional[Dict]:
        """Retorna uma UTC pelo ID"""
        query = "SELECT * FROM utcs WHERE utc_id = %s"
        return self.db.fetch_one(query, (utc_id,))
    
    def get_selected_utcs(self) -> Optional[List[Dict]]:
        """Retorna as UTCs selecionadas para o projeto (5 principais)"""
        query = """
            SELECT utc_id, utc_name, utc_offset, city_name, country, 
                   latitude, longitude, description 
            FROM utcs 
            LIMIT 5
        """
        return self.db.fetch_query(query)
    
    def insert_utc(self, utc_name: str, utc_offset: str, city_name: str, 
                   country: str, latitude: float, longitude: float, 
                   description: str = None) -> bool:
        """Insere uma nova UTC"""
        query = """
            INSERT INTO utcs (utc_name, utc_offset, city_name, country, 
                            latitude, longitude, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (utc_name, utc_offset, city_name, country, latitude, longitude, description)
        return self.db.execute_query(query, params)


class WeatherRepository:
    """Repositório para operações relacionadas a previsão de tempo"""
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db: Instância de DatabaseConnection
        """
        self.db = db
    
    def get_weather_by_utc_and_date(self, utc_id: int, forecast_date: str) -> Optional[Dict]:
        """Retorna previsão de tempo para uma UTC em uma data específica"""
        query = """
            SELECT * FROM weather_predictions 
            WHERE utc_id = %s AND forecast_date = %s
        """
        return self.db.fetch_one(query, (utc_id, forecast_date))
    
    def get_latest_weather(self, utc_id: int) -> Optional[Dict]:
        """Retorna a previsão de tempo mais recente para uma UTC"""
        query = """
            SELECT * FROM weather_predictions 
            WHERE utc_id = %s 
            ORDER BY forecast_date DESC 
            LIMIT 1
        """
        return self.db.fetch_one(query, (utc_id,))
    
    def get_all_weather_for_date(self, forecast_date: str) -> Optional[List[Dict]]:
        """Retorna previsão de tempo para todas as UTCs em uma data"""
        query = """
            SELECT w.*, u.city_name, u.country 
            FROM weather_predictions w
            JOIN utcs u ON w.utc_id = u.utc_id
            WHERE w.forecast_date = %s
            ORDER BY u.utc_name
        """
        return self.db.fetch_query(query, (forecast_date,))
    
    def insert_weather(self, utc_id: int, forecast_date: str, 
                      temperature: float, weather_condition: str,
                      precipitation: float = None, humidity: int = None,
                      wind_speed: float = None, climate_type: str = None,
                      image_url: str = None, video_url: str = None,
                      description: str = None) -> bool:
        """Insere uma previsão de tempo"""
        query = """
            INSERT INTO weather_predictions 
            (utc_id, forecast_date, temperature, weather_condition, 
             precipitation, humidity, wind_speed, climate_type, 
             image_url, video_url, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (utc_id, forecast_date, temperature, weather_condition,
                 precipitation, humidity, wind_speed, climate_type,
                 image_url, video_url, description)
        return self.db.execute_query(query, params)


class EventLogRepository:
    """Repositório para registros de eventos (logs)"""
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db: Instância de DatabaseConnection
        """
        self.db = db
    
    def get_all_logs(self, limit: int = 100) -> Optional[List[Dict]]:
        """Retorna todos os logs"""
        query = """
            SELECT * FROM event_logs 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return self.db.fetch_query(query, (limit,))
    
    def get_logs_by_type(self, log_type: str, limit: int = 50) -> Optional[List[Dict]]:
        """Retorna logs de um tipo específico"""
        query = """
            SELECT * FROM event_logs 
            WHERE log_type = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return self.db.fetch_query(query, (log_type, limit))
    
    def get_logs_by_date_range(self, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """Retorna logs em um intervalo de datas"""
        query = """
            SELECT * FROM event_logs 
            WHERE DATE(created_at) BETWEEN %s AND %s 
            ORDER BY created_at DESC
        """
        return self.db.fetch_query(query, (start_date, end_date))


class TaskRepository:
    """Repositório para gerenciamento de tarefas agendadas"""
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db: Instância de DatabaseConnection
        """
        self.db = db
    
    def get_active_tasks(self) -> Optional[List[Dict]]:
        """Retorna todas as tarefas ativas"""
        query = """
            SELECT * FROM scheduled_tasks 
            WHERE status = 'active' 
            ORDER BY schedule_time
        """
        return self.db.fetch_query(query)
    
    def get_task_by_name(self, task_name: str) -> Optional[Dict]:
        """Retorna uma tarefa pelo nome"""
        query = "SELECT * FROM scheduled_tasks WHERE task_name = %s"
        return self.db.fetch_one(query, (task_name,))
    
    def update_task_execution(self, task_id: int, execution_time: datetime) -> bool:
        """Atualiza o horário da última execução de uma tarefa"""
        query = """
            UPDATE scheduled_tasks 
            SET last_execution = %s, 
                next_execution = %s + INTERVAL '1 day'
            WHERE task_id = %s
        """
        return self.db.execute_query(query, (execution_time, execution_time, task_id))


class EmailHistoryRepository:
    """Repositório para histórico de emails"""
    
    def __init__(self, db: DatabaseConnection):
        """
        Inicializa o repositório
        
        Args:
            db: Instância de DatabaseConnection
        """
        self.db = db
    
    def insert_email_record(self, recipient: str, subject: str, 
                           status: str = 'sent', error_msg: str = None,
                           utc_ids: List[int] = None) -> bool:
        """Registra um email enviado"""
        query = """
            INSERT INTO email_history 
            (recipient_email, subject, status, error_message, utc_ids_included)
            VALUES (%s, %s, %s, %s, %s)
        """
        utc_json = json.dumps(utc_ids) if utc_ids else None
        params = (recipient, subject, status, error_msg, utc_json)
        return self.db.execute_query(query, params)
    
    def get_email_history(self, limit: int = 50) -> Optional[List[Dict]]:
        """Retorna histórico de emails"""
        query = """
            SELECT * FROM email_history 
            ORDER BY sent_at DESC 
            LIMIT %s
        """
        return self.db.fetch_query(query, (limit,))
