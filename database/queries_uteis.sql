-- ============================================================
-- QUERIES ÚTEIS - UTC Weather Reports
-- Exemplos de consultas para gerenciar o sistema
-- ============================================================

-- ============================================================
-- 1. CONSULTAS SOBRE UTCs
-- ============================================================

-- Listar todas as UTCs
SELECT utc_id, utc_name, city_name, country, utc_offset
FROM utcs
ORDER BY utc_offset;

-- Buscar UTC específica
SELECT * FROM utcs WHERE city_name LIKE '%Lisboa%';

-- Contar total de UTCs
SELECT COUNT(*) as total_utcs FROM utcs;

-- ============================================================
-- 2. CONSULTAS SOBRE PREVISÃO DE TEMPO
-- ============================================================

-- Previsão de hoje para todas as UTCs
SELECT 
    u.city_name,
    u.country,
    w.forecast_date,
    w.temperature,
    w.weather_condition,
    w.humidity,
    w.wind_speed,
    w.climate_type
FROM weather_predictions w
JOIN utcs u ON w.utc_id = u.utc_id
WHERE w.forecast_date = CURDATE()
ORDER BY u.utc_name;

-- Temperatura média por cidade
SELECT 
    u.city_name,
    AVG(w.temperature) as temp_media,
    MAX(w.temperature) as temp_maxima,
    MIN(w.temperature) as temp_minima
FROM weather_predictions w
JOIN utcs u ON w.utc_id = u.utc_id
GROUP BY u.city_name;

-- Regiões com clima tropical
SELECT 
    u.city_name,
    u.country,
    w.weather_condition,
    w.temperature,
    w.humidity
FROM weather_predictions w
JOIN utcs u ON w.utc_id = u.utc_id
WHERE w.climate_type = 'Tropical'
ORDER BY u.city_name;

-- Previsões de chuva
SELECT 
    u.city_name,
    u.utc_name,
    w.forecast_date,
    w.weather_condition,
    w.precipitation
FROM weather_predictions w
JOIN utcs u ON w.utc_id = u.utc_id
WHERE w.weather_condition LIKE '%Chuva%' OR w.weather_condition LIKE '%Chuvoso%'
ORDER BY u.city_name, w.forecast_date DESC;

-- ============================================================
-- 3. CONSULTAS SOBRE EVENTOS/LOGS
-- ============================================================

-- Listar últimos 10 eventos
SELECT 
    log_id,
    log_type,
    action_type,
    table_name,
    description,
    created_at
FROM event_logs
ORDER BY created_at DESC
LIMIT 10;

-- Eventos de inserção de UTCs
SELECT 
    log_id,
    description,
    new_values,
    created_at
FROM event_logs
WHERE action_type = 'INSERT' AND table_name = 'utcs'
ORDER BY created_at DESC;

-- Eventos por tipo
SELECT 
    log_type,
    COUNT(*) as total_eventos,
    MAX(created_at) as ultimo_evento
FROM event_logs
GROUP BY log_type
ORDER BY total_eventos DESC;

-- Timeline de eventos por data
SELECT 
    DATE(created_at) as data,
    COUNT(*) as total_eventos,
    GROUP_CONCAT(DISTINCT log_type) as tipos
FROM event_logs
GROUP BY DATE(created_at)
ORDER BY data DESC
LIMIT 30;

-- ============================================================
-- 4. CONSULTAS SOBRE TAREFAS AGENDADAS
-- ============================================================

-- Status de todas as tarefas
SELECT 
    task_id,
    task_name,
    task_type,
    schedule_time,
    status,
    last_execution,
    next_execution
FROM scheduled_tasks
ORDER BY schedule_time;

-- Tarefas ativas
SELECT * FROM scheduled_tasks WHERE status = 'active';

-- Próximas execuções
SELECT 
    task_name,
    task_type,
    next_execution
FROM scheduled_tasks
WHERE status = 'active'
ORDER BY next_execution ASC
LIMIT 5;

-- ============================================================
-- 5. CONSULTAS SOBRE EMAIL
-- ============================================================

-- Histórico de emails enviados
SELECT 
    email_id,
    recipient_email,
    subject,
    sent_at,
    status
FROM email_history
ORDER BY sent_at DESC
LIMIT 20;

-- Emails por status
SELECT 
    status,
    COUNT(*) as total,
    MAX(sent_at) as ultimo_envio
FROM email_history
GROUP BY status;

-- Destinatários que receberam emails
SELECT DISTINCT recipient_email FROM email_history;

-- UTCs incluídas nos últimos emails
SELECT 
    recipient_email,
    subject,
    sent_at,
    JSON_UNQUOTE(JSON_EXTRACT(utc_ids_included, '$[0]')) as utc_id
FROM email_history
WHERE utc_ids_included IS NOT NULL
ORDER BY sent_at DESC;

-- ============================================================
-- 6. CONSULTAS ANALÍTICAS
-- ============================================================

-- Relatório completo por UTC
SELECT 
    u.city_name,
    u.country,
    u.utc_name,
    u.utc_offset,
    COUNT(w.weather_id) as previsoes_registradas,
    AVG(w.temperature) as temperatura_media,
    MAX(w.weather_condition) as ultima_condicao
FROM utcs u
LEFT JOIN weather_predictions w ON u.utc_id = w.utc_id
GROUP BY u.utc_id, u.city_name, u.country, u.utc_name, u.utc_offset
ORDER BY u.city_name;

-- Regiões com mais previsões
SELECT 
    u.city_name,
    COUNT(w.weather_id) as total_previsoes,
    MAX(w.forecast_date) as ultima_atualizacao
FROM weather_predictions w
JOIN utcs u ON w.utc_id = u.utc_id
GROUP BY u.city_name
ORDER BY total_previsoes DESC;

-- Logs de erros/issues
SELECT * FROM event_logs
WHERE description LIKE '%erro%' 
   OR description LIKE '%Error%'
   OR description LIKE '%Failed%'
ORDER BY created_at DESC;

-- ============================================================
-- 7. MANUTENÇÃO
-- ============================================================

-- Limpar logs antigos (> 30 dias)
DELETE FROM event_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Limpar emails antigos (> 90 dias)
DELETE FROM email_history 
WHERE sent_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Resets de auto increment (após limpeza de dados)
-- ALTER TABLE event_logs AUTO_INCREMENT = 1;
-- ALTER TABLE email_history AUTO_INCREMENT = 1;

-- ============================================================
-- 8. ESTATÍSTICAS DO SISTEMA
-- ============================================================

-- Resumo geral
SELECT 
    (SELECT COUNT(*) FROM utcs) as total_utcs,
    (SELECT COUNT(*) FROM weather_predictions) as total_previsoes,
    (SELECT COUNT(*) FROM event_logs) as total_eventos,
    (SELECT COUNT(*) FROM email_history) as total_emails,
    (SELECT COUNT(*) FROM scheduled_tasks) as total_tarefas;

-- Cobertura de dados
SELECT 
    u.city_name,
    COUNT(w.weather_id) as dias_com_previsao,
    MAX(w.forecast_date) as ultima_atualizacao,
    DATEDIFF(CURDATE(), MAX(w.forecast_date)) as dias_sem_atualizar
FROM utcs u
LEFT JOIN weather_predictions w ON u.utc_id = w.utc_id
GROUP BY u.city_name
ORDER BY dias_sem_atualizar DESC;

-- Performance de envio de emails
SELECT 
    DATE(sent_at) as data,
    status,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'sent' THEN 1 END) as enviados,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as falhados
FROM email_history
GROUP BY DATE(sent_at), status
ORDER BY data DESC;

-- ============================================================
-- 9. VIEWS ÚTEIS
-- ============================================================

-- View: Previsão atual para todas as UTCs
CREATE OR REPLACE VIEW vw_previsao_atual AS
SELECT 
    u.utc_id,
    u.city_name,
    u.country,
    u.utc_name,
    u.utc_offset,
    w.temperature,
    w.weather_condition,
    w.humidity,
    w.wind_speed,
    w.climate_type,
    w.forecast_date
FROM utcs u
LEFT JOIN weather_predictions w ON u.utc_id = w.utc_id 
    AND w.forecast_date = (
        SELECT MAX(forecast_date) 
        FROM weather_predictions 
        WHERE utc_id = u.utc_id
    );

-- View: Histórico de eventos por hora
CREATE OR REPLACE VIEW vw_eventos_por_hora AS
SELECT 
    DATE(created_at) as data,
    HOUR(created_at) as hora,
    log_type,
    COUNT(*) as total_eventos
FROM event_logs
GROUP BY DATE(created_at), HOUR(created_at), log_type
ORDER BY data DESC, hora DESC;

-- Usar as views:
-- SELECT * FROM vw_previsao_atual;
-- SELECT * FROM vw_eventos_por_hora;

-- ============================================================
-- FIM DO ARQUIVO DE QUERIES
-- ============================================================
