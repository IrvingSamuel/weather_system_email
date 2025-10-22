"""
Módulo de Jobs Agendados (Scheduler)
Gerencia tarefas agendadas usando APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from typing import Callable, Dict, Any
from datetime import datetime
from config.config import SCHEDULED_JOBS, LOGGING_CONFIG

# Configurar logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    filename=LOGGING_CONFIG['file']
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Classe para gerenciar tarefas agendadas"""
    
    def __init__(self):
        """Inicializa o scheduler"""
        self.scheduler = BackgroundScheduler()
        self.jobs_registry = {}
    
    def add_job(self, job_name: str, func: Callable, **trigger_args) -> bool:
        """
        Adiciona um novo job agendado
        
        Args:
            job_name: Nome do job
            func: Função a ser executada
            **trigger_args: Argumentos para CronTrigger
        
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            trigger = CronTrigger(**trigger_args)
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_name,
                name=job_name,
                replace_existing=True,
                max_instances=1
            )
            
            self.jobs_registry[job_name] = {
                'job': job,
                'function': func,
                'created_at': datetime.now(),
                'last_run': None,
                'next_run': job.next_run_time
            }
            
            logger.info(f"Job '{job_name}' adicionado com sucesso")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao adicionar job '{job_name}': {e}")
            return False
    
    def start(self) -> bool:
        """
        Inicia o scheduler
        
        Returns:
            bool: True se iniciado com sucesso
        """
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler iniciado com sucesso")
                self._log_scheduled_jobs()
                return True
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar scheduler: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Para o scheduler
        
        Returns:
            bool: True se parado com sucesso
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler parado com sucesso")
                return True
            return True
        except Exception as e:
            logger.error(f"Erro ao parar scheduler: {e}")
            return False
    
    def get_job_status(self, job_name: str) -> Dict[str, Any]:
        """
        Retorna o status de um job
        
        Args:
            job_name: Nome do job
        
        Returns:
            Dict: Status do job
        """
        if job_name in self.jobs_registry:
            job_info = self.jobs_registry[job_name]
            return {
                'name': job_name,
                'status': 'running' if self.scheduler.running else 'stopped',
                'next_run': job_info['next_run'],
                'created_at': job_info['created_at'],
                'last_run': job_info['last_run']
            }
        return None
    
    def get_all_jobs_status(self) -> Dict[str, Any]:
        """
        Retorna status de todos os jobs
        
        Returns:
            Dict: Status de todos os jobs
        """
        jobs_status = {}
        for job_name in self.jobs_registry:
            jobs_status[job_name] = self.get_job_status(job_name)
        return jobs_status
    
    def remove_job(self, job_name: str) -> bool:
        """
        Remove um job agendado
        
        Args:
            job_name: Nome do job
        
        Returns:
            bool: True se removido com sucesso
        """
        try:
            self.scheduler.remove_job(job_name)
            del self.jobs_registry[job_name]
            logger.info(f"Job '{job_name}' removido com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover job '{job_name}': {e}")
            return False
    
    def _log_scheduled_jobs(self):
        """Registra todos os jobs agendados no log"""
        logger.info("=== JOBS AGENDADOS ===")
        for job in self.scheduler.get_jobs():
            logger.info(f"Job: {job.name} | Próxima execução: {job.next_run_time}")
        logger.info("=====================")


class SchedulerManager:
    """Gerenciador centralizado de tarefas agendadas"""
    
    def __init__(self, db_connection=None):
        """
        Inicializa o gerenciador
        
        Args:
            db_connection: Conexão com banco de dados (opcional)
        """
        self.scheduler = TaskScheduler()
        self.db = db_connection
    
    def initialize_jobs(self, callbacks: Dict[str, Callable]) -> bool:
        """
        Inicializa todos os jobs baseado na configuração
        
        Args:
            callbacks: Dicionário com funções de callback {nome_job: funcao}
        
        Returns:
            bool: True se inicializado com sucesso
        """
        try:
            for job_name, job_config in SCHEDULED_JOBS.items():
                if job_name not in callbacks:
                    logger.warning(f"Callback não encontrado para job '{job_name}'")
                    continue
                
                func = callbacks[job_name]
                
                # Preparar argumentos para CronTrigger
                trigger_args = {
                    key: value for key, value in job_config.items()
                    if key not in ['function', 'description']
                }
                
                # Remover 'trigger' se presente
                trigger_args.pop('trigger', None)
                
                self.scheduler.add_job(job_name, func, **trigger_args)
            
            logger.info(f"Total de {len(self.scheduler.jobs_registry)} jobs inicializados")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao inicializar jobs: {e}")
            return False
    
    def start_scheduler(self) -> bool:
        """
        Inicia o scheduler
        
        Returns:
            bool: True se iniciado com sucesso
        """
        return self.scheduler.start()
    
    def stop_scheduler(self) -> bool:
        """
        Para o scheduler
        
        Returns:
            bool: True se parado com sucesso
        """
        return self.scheduler.stop()
    
    def is_running(self) -> bool:
        """
        Verifica se o scheduler está em execução
        
        Returns:
            bool: True se está em execução
        """
        return self.scheduler.scheduler.running


# Wrapper para atualizar informações de job no banco de dados
def update_job_execution_info(db_connection, task_id: int, execution_time: datetime = None):
    """
    Atualiza informações de execução de um job no banco de dados
    
    Args:
        db_connection: Conexão com banco de dados
        task_id: ID da tarefa
        execution_time: Hora da execução
    """
    try:
        from src.database import TaskRepository
        
        if execution_time is None:
            execution_time = datetime.now()
        
        task_repo = TaskRepository(db_connection)
        task_repo.update_task_execution(task_id, execution_time)
        
        logger.info(f"Informações de execução da tarefa {task_id} atualizadas")
    except Exception as e:
        logger.error(f"Erro ao atualizar informações de execução: {e}")
