"""
Pacote src - Módulos principais da aplicação
"""

__version__ = "1.0.0"
__author__ = "Equipe de Desenvolvimento"

from .database import DatabaseConnection, UTCRepository, WeatherRepository
from .report_generator import ReportGenerator
from .email_sender import EmailSender
from .scheduler import TaskScheduler, SchedulerManager

__all__ = [
    'DatabaseConnection',
    'UTCRepository',
    'WeatherRepository',
    'ReportGenerator',
    'EmailSender',
    'TaskScheduler',
    'SchedulerManager'
]
