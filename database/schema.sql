-- ============================================================
-- BANCO DE DADOS: UTC Weather Reports
-- Descrição: Sistema para gerenciar informações de UTCs e previsão de tempo
-- ============================================================

-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS utc_weather_db;
USE utc_weather_db;

-- ============================================================
-- TABELA: utcs
-- Descrição: Armazena informações das Zonas Horárias (UTCs)
-- ============================================================
CREATE TABLE IF NOT EXISTS utcs (
    utc_id INT PRIMARY KEY AUTO_INCREMENT,
    utc_name VARCHAR(50) NOT NULL UNIQUE,
    utc_offset VARCHAR(10) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: weather_predictions
-- Descrição: Armazena previsões de tempo por UTC
-- ============================================================
CREATE TABLE IF NOT EXISTS weather_predictions (
    weather_id INT PRIMARY KEY AUTO_INCREMENT,
    utc_id INT NOT NULL,
    forecast_date DATE NOT NULL,
    temperature DECIMAL(5, 2),
    weather_condition VARCHAR(100),
    precipitation DECIMAL(5, 2),
    humidity INT,
    wind_speed DECIMAL(5, 2),
    climate_type VARCHAR(50),
    image_url VARCHAR(500),
    video_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utc_id) REFERENCES utcs(utc_id) ON DELETE CASCADE,
    UNIQUE KEY unique_utc_date (utc_id, forecast_date)
);

-- ============================================================
-- TABELA: event_logs
-- Descrição: Registra todos os eventos e ações do sistema (Triggers)
-- ============================================================
CREATE TABLE IF NOT EXISTS event_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100),
    action_type VARCHAR(20),
    affected_utc_id INT,
    old_values JSON,
    new_values JSON,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: scheduled_tasks
-- Descrição: Gerencia tarefas agendadas (jobs) do sistema
-- ============================================================
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    schedule_time TIME,
    schedule_day VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    last_execution TIMESTAMP,
    next_execution TIMESTAMP,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABELA: email_history
-- Descrição: Registra histórico de emails enviados
-- ============================================================
CREATE TABLE IF NOT EXISTS email_history (
    email_id INT PRIMARY KEY AUTO_INCREMENT,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent',
    error_message TEXT,
    utc_ids_included JSON
);

-- ============================================================
-- TRIGGER: log_utc_insert
-- Descrição: Registra inserções na tabela utcs
-- ============================================================
DELIMITER //

CREATE TRIGGER log_utc_insert
AFTER INSERT ON utcs
FOR EACH ROW
BEGIN
    INSERT INTO event_logs (log_type, table_name, action_type, affected_utc_id, new_values, description)
    VALUES ('UTC_CHANGE', 'utcs', 'INSERT', NEW.utc_id, 
            JSON_OBJECT('utc_name', NEW.utc_name, 'city_name', NEW.city_name, 'country', NEW.country),
            CONCAT('Nova UTC criada: ', NEW.city_name, ' (', NEW.utc_name, ')'));
END //

-- ============================================================
-- TRIGGER: log_utc_update
-- Descrição: Registra atualizações na tabela utcs
-- ============================================================
CREATE TRIGGER log_utc_update
AFTER UPDATE ON utcs
FOR EACH ROW
BEGIN
    INSERT INTO event_logs (log_type, table_name, action_type, affected_utc_id, old_values, new_values, description)
    VALUES ('UTC_CHANGE', 'utcs', 'UPDATE', NEW.utc_id,
            JSON_OBJECT('utc_name', OLD.utc_name, 'city_name', OLD.city_name),
            JSON_OBJECT('utc_name', NEW.utc_name, 'city_name', NEW.city_name),
            CONCAT('UTC atualizada: ', NEW.city_name));
END //

-- ============================================================
-- TRIGGER: log_weather_insert
-- Descrição: Registra inserções de previsão de tempo
-- ============================================================
CREATE TRIGGER log_weather_insert
AFTER INSERT ON weather_predictions
FOR EACH ROW
BEGIN
    INSERT INTO event_logs (log_type, table_name, action_type, affected_utc_id, new_values, description)
    VALUES ('WEATHER_UPDATE', 'weather_predictions', 'INSERT', NEW.utc_id,
            JSON_OBJECT('temperature', NEW.temperature, 'weather_condition', NEW.weather_condition, 'climate_type', NEW.climate_type),
            CONCAT('Previsão de tempo criada para UTC ID: ', NEW.utc_id));
END //

-- ============================================================
-- TRIGGER: log_task_execution
-- Descrição: Registra execução de tarefas agendadas
-- ============================================================
CREATE TRIGGER log_task_execution
AFTER UPDATE ON scheduled_tasks
FOR EACH ROW
BEGIN
    IF NEW.last_execution != OLD.last_execution THEN
        INSERT INTO event_logs (log_type, table_name, action_type, description)
        VALUES ('TASK_EXECUTION', 'scheduled_tasks', 'UPDATE',
                CONCAT('Tarefa executada: ', NEW.task_name, ' às ', NEW.last_execution));
    END IF;
END //

DELIMITER ;

-- ============================================================
-- ÍNDICES para otimização de queries
-- ============================================================
CREATE INDEX idx_weather_utc_id ON weather_predictions(utc_id);
CREATE INDEX idx_weather_date ON weather_predictions(forecast_date);
CREATE INDEX idx_event_logs_type ON event_logs(log_type);
CREATE INDEX idx_event_logs_timestamp ON event_logs(created_at);
CREATE INDEX idx_email_history_status ON email_history(status);

-- ============================================================
-- DADOS INICIAIS
-- ============================================================

-- Inserir 5 UTCs diferentes para o projeto
INSERT INTO utcs (utc_name, utc_offset, city_name, country, latitude, longitude, description) VALUES
('UTC-3', '-03:00', 'Brasília', 'Brasil', -15.7942, -47.8822, 'Capital do Brasil - Região do Cerrado'),
('UTC+1', '+01:00', 'Lisboa', 'Portugal', 38.7223, -9.1393, 'Capital de Portugal - Região Costeira'),
('UTC+8', '+08:00', 'Singapura', 'Singapura', 1.3521, 103.8198, 'Cidade-Estado Tropical - Sudeste Asiático'),
('UTC+12', '+12:00', 'Auckland', 'Nova Zelândia', -37.0882, 174.8860, 'Maior cidade da Nova Zelândia - Oceania'),
('UTC-5', '-05:00', 'Nova York', 'Estados Unidos', 40.7128, -74.0060, 'Metrópole Americana - Leste do EUA');

-- Inserir tarefas agendadas
INSERT INTO scheduled_tasks (task_name, task_type, schedule_time, schedule_day, status, description) VALUES
('Gerar Relatório Diário', 'REPORT_GENERATION', '08:00:00', 'MON,TUE,WED,THU,FRI', 'active', 'Gera relatório diário pela manhã'),
('Enviar Email para Equipe', 'EMAIL_DISPATCH', '08:30:00', 'MON,TUE,WED,THU,FRI', 'active', 'Envia email com relatório para a equipe'),
('Atualizar Previsão de Tempo', 'WEATHER_UPDATE', '06:00:00', 'DAILY', 'active', 'Atualiza dados de previsão de tempo'),
('Limpeza de Logs', 'LOG_CLEANUP', '00:00:00', 'SUN', 'active', 'Remove logs antigos do sistema');
