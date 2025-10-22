"""
Arquivo de Configuração do Projeto UTC Weather Reports
"""

import os
from datetime import time

# ============================================================
# CONFIGURAÇÕES DO BANCO DE DADOS - POSTGRESQL
# ============================================================

DB_CONFIG = {
    'host': 'localhost',
    'user': 'vscode',             # Usuário pgAdmin
    'password': 'vscodeaccess',   # Senha pgAdmin
    'database': 'utc_weather_db',
    'port': 5432,                 # Porta padrão PostgreSQL
}

# String de conexão para psycopg2
DB_CONNECTION_STRING = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ============================================================
# CONFIGURAÇÕES DE EMAIL - HOSTINGER
# ============================================================

EMAIL_CONFIG = {
    'smtp_server': 'smtp.hostinger.com',
    'smtp_port': 465,                 # Porta SSL
    'sender_email': 'no-reply@rezum.me',
    'sender_password': 'Rezumme@3',
    'use_tls': False,                 # Usar SSL, não TLS
    'use_ssl': True,                  # SSL na porta 465
}

# ============================================================
# CONFIGURAÇÕES DE API CLIMA - WEATHERAPI.COM
# ============================================================

WEATHER_API_CONFIG = {
    'api_key': '1ef79bd0a0394189a1404522252210',
    'base_url': 'http://api.weatherapi.com/v1',
    'timeout': 10,  # Timeout em segundos
    'cache_duration': 3600,  # Cache de 1 hora (em segundos)
}

# Lista de destinatários
RECIPIENTS = [
    'sync.irvingsamuel@gmail.com',      # Email do aluno
    'paulopaes216@gmail.com',           # Email do aluno
    'georgeluismoraes@gmail.com',       # Email do aluno
    'rafhaeliggor@gmail.com',           # Email do aluno
    'francisco.vital@unima.edu.br'      # Email do professor
]

# ============================================================
# CONFIGURAÇÕES DE JOBS AGENDADOS
# ============================================================

SCHEDULED_JOBS = {
    'report_generation': {
        'function': 'generate_daily_report',
        'trigger': 'cron',
        'hour': 8,
        'minute': 0,
        'day_of_week': 'mon-fri',
        'description': 'Gera relatório diário'
    },
    'email_dispatch': {
        'function': 'send_report_email',
        'trigger': 'cron',
        'hour': 8,
        'minute': 30,
        'day_of_week': 'mon-fri',
        'description': 'Envia email com relatório'
    },
    'weather_update': {
        'function': 'update_weather_data',
        'trigger': 'cron',
        'hour': 6,
        'minute': 0,
        'description': 'Atualiza previsão de tempo'
    },
    'log_cleanup': {
        'function': 'cleanup_old_logs',
        'trigger': 'cron',
        'day_of_week': 'sun',
        'hour': 0,
        'minute': 0,
        'description': 'Limpa logs antigos'
    }
}

# ============================================================
# CONFIGURAÇÕES DE CAMINHOS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Criar diretórios se não existirem
for directory in [TEMPLATES_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================
# CONFIGURAÇÕES DE LOGGING
# ============================================================

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, 'app.log'),
    'max_bytes': 10485760,  # 10MB
    'backup_count': 10
}

# ============================================================
# UTCs SELECIONADAS PARA O PROJETO
# ============================================================

SELECTED_UTCS = [
    {
        'utc_id': 1,
        'utc_name': 'UTC-3',
        'city': 'Brasília',
        'country': 'Brasil',
        'description': 'Capital do Brasil - Região do Cerrado'
    },
    {
        'utc_id': 2,
        'utc_name': 'UTC-12',
        'city': 'Baker Island',
        'country': 'Estados Unidos',
        'description': 'Ilha desabitada localizada no Oceano Pacífico Central, território dos EUA'
    },
    {
        'utc_id': 3,
        'utc_name': 'UTC-11',
        'city': 'Pago Pago',
        'country': 'Samoa Americana',
        'description': 'Capital da Samoa Americana, território dos Estados Unidos no Pacífico Sul'
    },
    {
        'utc_id': 4,
        'utc_name': 'UTC-5',
        'city': 'Bogotá',
        'country': 'Colômbia',
        'description': 'Capital da Colômbia, situada nos Andes, conhecida por sua rica cultura e história'
    },
    {
        'utc_id': 5,
        'utc_name': 'UTC-1',
        'city': 'Cabo Verde',
        'country': 'Cabo Verde',
        'description': 'País insular localizado no Oceano Atlântico, conhecido por suas ilhas vulcânicas e cultura criola'
    },
    {
        'utc_id': 6,
        'utc_name': 'UTC+11',
        'city': 'Honiara',
        'country': 'Ilhas Salomão',
        'description': 'Capital das Ilhas Salomão, localizada na Ilha de Guadalcanal, no Oceano Pacífico'
    }
]

# ============================================================
# CONFIGURAÇÕES DE RELATÓRIOS
# ============================================================

REPORT_CONFIG = {
    'format': 'html',
    'include_images': True,
    'include_videos': True,
    'timezone_info': True,
    'weather_details': True
}


# ============================================================
# DESABILITAR EMAIL TEMPORARIAMENTE
# ============================================================
EMAIL_DISABLED = False  # Email HABILITADO com Hostinger
