# 🌍 UTC Weather Reports - Sistema Completo de Gestão Meteorológica

Sistema de gestão de zonas horárias com **dados meteorológicos em tempo real**, interface gráfica moderna em **modo escuro**, PostgreSQL e automação completa de relatórios por email.

## ✨ Funcionalidades Principais

- 🌐 **Dados Reais de Clima** - Integração com WeatherAPI.com
- 🇧🇷 **Tradução Automática** - 60+ condições climáticas em Português
- 🌙 **Interface Modo Escuro** - Design moderno e profissional
- � **Relatórios HTML Dinâmicos** - Gerados com timestamp único
- 📧 **Envio Automático de Email** - SMTP Hostinger configurado
- 🔄 **Auto-atualização** - Dados sempre frescos da API
- 🗄️ **PostgreSQL 17.5** - Banco de dados robusto

## �🚀 Início Rápido

### 1. Pré-requisitos
- PostgreSQL 17.5+ instalado e rodando
- Python 3.13+
- Conta WeatherAPI.com (gratuita)
- Email SMTP configurado (opcional)

### 2. Setup

```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados

**Opção A - Via pgAdmin:**
1. Abra pgAdmin: `http://localhost:5050`
2. Crie database: `utc_weather_db`
3. Execute: `database/schema_postgresql.sql`

**Opção B - Via Script:**
```powershell
python setup_schema.py
```

### 4. Popular UTCs Corretas

```powershell
python populate_correct_utcs.py
```

Isso cadastrará as 5 UTCs do projeto:
- UTC-12: Baker Island, USA
- UTC-11: Pago Pago, Samoa Americana
- UTC-5: Bogotá, Colômbia
- UTC-1: Cabo Verde
- UTC+11: Honiara, Ilhas Salomão

### 5. Configurar API e Email

Edite `config/config.py`:

```python
# API de Clima (WeatherAPI.com)
WEATHER_API_CONFIG = {
    'api_key': 'SUA_API_KEY_AQUI',  # Obtenha em weatherapi.com
    'base_url': 'http://api.weatherapi.com/v1',
    'timeout': 10,
}

# Email (Hostinger ou outro SMTP)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.hostinger.com',
    'smtp_port': 465,
    'sender_email': 'seu-email@dominio.com',
    'sender_password': 'sua-senha',
    'use_ssl': True,
}

# Destinatários dos relatórios
RECIPIENTS = [
    'destinatario1@email.com',
    'destinatario2@email.com'
]
```

### 6. Iniciar a Aplicação

```powershell
# Interface Gráfica (recomendado)
.\launch-gui-simple.ps1

# Ou diretamente
python -m src.gui
```

## 📂 Estrutura do Projeto

```
Banco de dados/
├── src/
│   ├── gui.py                    # Interface gráfica PyQt5 (Dark Mode)
│   ├── database.py               # Conexão e repositórios PostgreSQL
│   ├── report_generator.py       # Gera relatórios HTML com timestamp
│   ├── email_sender.py           # Envio de emails SMTP (SSL)
│   └── weather_api.py            # Cliente WeatherAPI.com + Traduções
├── config/
│   └── config.py                 # Todas as configurações do sistema
├── database/
│   ├── schema_postgresql.sql     # Schema completo do banco
│   └── docs/                     # Documentação do modelo de dados
├── templates/
│   └── report_template.html      # Template Jinja2 para relatórios
├── reports/                      # Relatórios HTML gerados
├── logs/                         # Arquivos de log do sistema
├── requirements.txt              # Dependências Python
├── launch-gui-simple.ps1         # Launcher da GUI
├── setup_schema.py               # Setup automático do banco
├── populate_correct_utcs.py      # Popular UTCs do projeto
├── update_weather_from_api.py    # Atualizar clima via API
├── test_report.py                # Teste de geração de relatório
├── test_email_hostinger.py       # Teste de envio de email
├── test_system.py                # Testes completos do sistema
├── SISTEMA_COMPLETO.md           # Documentação detalhada
└── README.md                     # Este arquivo
```

## 🎨 Interface Gráfica - Modo Escuro 🌙

A GUI possui **7 abas** organizadas com tema escuro moderno:

### 📊 Dashboard
- Status de conexão com banco de dados
- UTCs cadastradas
- Log de atividades em tempo real
- Botões de ação rápida

### 📍 UTCs
- Tabela com todas as zonas horárias
- Informações: cidade, país, offset, descrição
- Gerenciamento de UTCs (adicionar/editar/deletar)

### 🌤️ Previsão
- Visualização de dados meteorológicos
- Filtros por UTC
- Detalhes: temperatura, condição, umidade, vento

### 📄 Relatórios
- **Gerar Relatório com Dados Atuais** (botão verde)
- Lista de todos os relatórios gerados
- **Abrir Último Gerado** (botão destaque)
- Visualizar qualquer relatório (duplo clique)
- Abrir pasta de relatórios

### 📧 Email
- Configurar destinatários
- Assunto e corpo personalizáveis
- Enviar relatório com anexo automático
- Feedback visual de sucesso/erro

### 📋 Logs
- Histórico completo de eventos
- Filtros por tipo de operação
- Exportação de logs

### ⚙️ Configurações
- Conexão com banco de dados
- Configurações SMTP
- Testes de conectividade

## 🗄️ Banco de Dados PostgreSQL

### Tabelas Principais

- **utcs** - Informações de zonas horárias
  - `utc_id`, `utc_name`, `city_name`, `country`, `utc_offset`
  - `description`, `image_url`, `video_url`
  
- **weather_predictions** - Dados meteorológicos por UTC
  - `prediction_id`, `utc_id`, `forecast_date`
  - `temperature`, `weather_condition`, `humidity`, `wind_speed`
  - `climate_type`, `last_updated`

- **event_logs** - Log automático de todas operações
  - Trigger: registra INSERT, UPDATE, DELETE
  - `event_id`, `table_name`, `operation_type`, `event_timestamp`

- **scheduled_tasks** - Tarefas agendadas
  - `task_id`, `task_name`, `schedule_time`, `is_active`

- **email_history** - Histórico de emails enviados
  - `email_id`, `subject`, `recipients`, `sent_at`, `status`

### UTCs Cadastradas (Projeto)

| UTC | Cidade | País | Offset |
|-----|--------|------|--------|
| UTC-12 | Baker Island | Estados Unidos | -12:00 |
| UTC-11 | Pago Pago | Samoa Americana | -11:00 |
| UTC-5 | Bogotá | Colômbia | -05:00 |
| UTC-1 | Cabo Verde | Cabo Verde | -01:00 |
| UTC+11 | Honiara | Ilhas Salomão | +11:00 |

## 🌐 Integração com WeatherAPI.com

### Como Funciona

1. **Cada geração de relatório**:
   - 🌐 Conecta na WeatherAPI.com
   - 🔄 Busca clima ATUAL de todas as UTCs
   - 🇧🇷 Traduz condições para português
   - 💾 Salva no banco de dados
   - 📝 Gera relatório HTML

2. **Dados obtidos**:
   - Temperatura atual (°C)
   - Condição climática (traduzida)
   - Umidade (%)
   - Velocidade do vento (km/h)
   - Tipo de clima (classificação)

3. **Tradução Automática**:
   ```
   "Clear" → "Limpo"
   "Sunny" → "Ensolarado"
   "Partly cloudy" → "Parcialmente Nublado"
   "Light rain" → "Chuva Leve"
   "Moderate rain" → "Chuva Moderada"
   ... 60+ traduções
   ```

## 📊 Relatórios HTML

### Características

- **Timestamp único**: `relatorio_utc_2025-10-21_22-02-26.html`
- **Sem sobrescrita**: Cada relatório é único
- **Design responsivo**: Funciona em mobile/desktop
- **Dados em tempo real**: Sempre atualizados da API
- **Idioma**: 100% em Português
- **Estilo profissional**: Cards coloridos, gradientes, ícones

### Conteúdo do Relatório

Para cada UTC, o relatório inclui:
- 📍 Cidade e país
- 🌍 Zona horária e offset
- 📝 Descrição da região
- 🌡️ Temperatura atual
- ☁️ Condição climática
- 💧 Umidade
- 💨 Velocidade do vento
- 🎨 Tipo de clima
- 🖼️ Links para imagens/vídeos

### Como Visualizar

1. **Via GUI**: Aba "Relatórios" → "Abrir Último Gerado"
2. **Via pasta**: `reports/` → duplo clique no HTML
3. **Via código**: Relatórios abrem automaticamente no navegador

## � Sistema de Email

### Configuração (Hostinger)

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.hostinger.com',
    'smtp_port': 465,                    # SSL
    'sender_email': 'no-reply@rezum.me',
    'sender_password': 'sua-senha',
    'use_ssl': True,
}
```

### Email HTML Estilizado

Cada email enviado contém:
- 🎨 **Header colorido** com gradiente
- 📊 **Cards para cada UTC** com dados climáticos
- 🌡️ **Grid de informações** meteorológicas
- 📎 **Relatório HTML em anexo**
- 📱 **Design responsivo** (mobile-friendly)
- 🔗 **Links para mídia** das regiões

### Como Enviar

**Via GUI:**
1. Gere um relatório primeiro
2. Clique "📧 Enviar Email" (toolbar ou aba Email)
3. Confirme destinatários
4. Aguarde confirmação

**Via código:**
```powershell
python test_email_hostinger.py  # Teste de email
```

### Destinatários

Configure em `config/config.py`:
```python
RECIPIENTS = [
    'sync.irvingsamuel@gmail.com',
    'francisco.vital@unima.edu.br'
]
```

## 🧪 Testes Disponíveis

### 1. Teste Completo do Sistema
```powershell
python test_system.py
```
Verifica: conexão BD, UTCs, clima, relatórios, logs

### 2. Teste de Geração de Relatório
```powershell
python test_report.py
```
- Busca dados da API
- Traduz para português
- Gera relatório HTML
- Exibe tamanho e localização

### 3. Teste de Email
```powershell
python test_email_hostinger.py
```
- Conecta SMTP Hostinger
- Envia email de teste
- Confirma entrega

### 4. Verificar Dados de UTCs
```powershell
python verify_utc_data.py
```
Lista todas as UTCs e dados meteorológicos

### 5. Atualizar Clima Manualmente
```powershell
python update_weather_from_api.py
```
Atualiza todos os dados da API sem gerar relatório

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| "relation 'utcs' does not exist" | Execute `python setup_schema.py` ou rode `schema_postgresql.sql` no pgAdmin |
| "connection refused" | PostgreSQL não está rodando. Inicie o serviço PostgreSQL |
| GUI não abre | Execute `pip install PyQt5==5.15.10` |
| "No module named 'psycopg2'" | Execute `pip install psycopg2-binary==2.9.11` |
| Email não envia | Verifique credenciais SMTP em `config/config.py` |
| "ModuleNotFoundError: No module named 'src'" | Use `python -m src.gui` ao invés de `python src/gui.py` |
| API retorna erro 401 | API Key inválida. Verifique em `config/config.py` |
| Condições em inglês | Sistema de tradução ativo. Se aparecer inglês, adicione em `WEATHER_TRANSLATIONS` |
| Relatório não abre | Verifique se navegador padrão está configurado no Windows |
| Email na pasta SPAM | Marque como "Não é spam" no primeiro recebimento |

## 📦 Dependências (requirements.txt)

```
PyQt5==5.15.10              # Interface gráfica
psycopg2-binary==2.9.11     # Driver PostgreSQL
APScheduler==3.10.4         # Agendador de tarefas
Jinja2==3.1.2               # Templates HTML
python-dateutil==2.8.2      # Utilidades de data
pytz==2023.3                # Zonas horárias
requests==2.32.3            # Requisições HTTP (WeatherAPI)
```

### Instalação Manual (se necessário)

```powershell
pip install PyQt5==5.15.10
pip install psycopg2-binary==2.9.11
pip install APScheduler==3.10.4
pip install Jinja2==3.1.2
pip install python-dateutil==2.8.2
pip install pytz==2023.3
pip install requests==2.32.3
```

## 🎯 Fluxo de Uso Completo

### 1️⃣ **Primeira Execução**
```powershell
# 1. Criar banco de dados
python setup_schema.py

# 2. Popular UTCs do projeto
python populate_correct_utcs.py

# 3. Atualizar clima da API
python update_weather_from_api.py

# 4. Abrir GUI
.\launch-gui-simple.ps1
```

### 2️⃣ **Gerar e Enviar Relatório**
1. Abra a GUI
2. Aba **"Relatórios"**
3. Clique **"Gerar Relatório com Dados Atuais"**
4. Aguarde (busca API + gera HTML)
5. Clique **"Sim"** para abrir
6. Clique **"Enviar Email"** (toolbar)
7. Confirme destinatários
8. Verifique emails enviados

### 3️⃣ **Visualizar Relatórios Anteriores**
1. Aba **"Relatórios"**
2. Lista mostra todos os relatórios gerados
3. **Duplo clique** para abrir qualquer um
4. Ou **"Abrir Último Gerado"** para o mais recente
5. Ou **"Abrir Pasta"** para ver todos os arquivos

### 4️⃣ **Atualizar Dados Manualmente**
```powershell
# Apenas atualizar clima (sem gerar relatório)
python update_weather_from_api.py
```

## 📸 Screenshots

### Interface Modo Escuro
- Fundo: `#1e1e1e` (preto suave)
- Texto: `#e0e0e0` (branco suave)
- Botões: `#0d6efd` (azul moderno)
- Tabelas: `#2d2d2d` (cinza escuro)

### Relatório HTML
- Design responsivo
- Cards coloridos
- Gradientes suaves
- Ícones modernos
- Grid organizado

## 🔐 Credenciais Padrão

### PostgreSQL
```
Host:     localhost
Port:     5432
Database: utc_weather_db
User:     vscode
Password: vscodeaccess
```

### Email (Hostinger)
```
SMTP:     smtp.hostinger.com
Port:     465 (SSL)
Email:    no-reply@rezum.me
Password: [configurar em config.py]
```

### WeatherAPI.com
```
API Key:  [obter gratuitamente em weatherapi.com]
Base URL: http://api.weatherapi.com/v1
```

## 👥 Contatos

- **Aluno**: sync.irvingsamuel@gmail.com
- **Professor**: francisco.vital@unima.edu.br

## ✅ Status

- ✅ Sistema 100% funcional
- ✅ 6/6 testes passaram
- ✅ Pronto para produção
- ✅ Interface responsiva
- ✅ Automação completa

---

**Versão**: 1.0 Final | **Status**: Pronto para Produção

##  Documentação Adicional

- **SISTEMA_COMPLETO.md** - Documentação técnica detalhada
- **database/docs/** - Modelo de dados e diagramas
- **config/config.py** - Todas as configurações comentadas

##  Contribuindo

Este é um projeto acadêmico. Para sugestões ou melhorias:
1. Fork o repositório
2. Crie uma branch
3. Commit suas mudanças
4. Abra um Pull Request

##  Autores

- **Aluno**: Irving Samuel - sync.irvingsamuel@gmail.com
- **Professor**: Francisco Vital - francisco.vital@unima.edu.br
- **Instituição**: UNIMA
- **Disciplina**: Banco de Dados
- **Período**: Outubro/2025

##  Licença

Este projeto é para fins acadêmicos.

##  Status do Sistema

-  **Banco de Dados**: PostgreSQL 17.5 - 5 UTCs cadastradas
-  **API**: WeatherAPI.com - Integração completa
-  **Tradução**: 60+ condições em Português
-  **Relatórios**: HTML com timestamp único
-  **Email**: SMTP Hostinger SSL funcionando
-  **GUI**: Modo escuro moderno e responsivo
-  **Testes**: 100% aprovados
-  **Pronto para Produção**: Sistema completo e funcional

---

**Versão**: 1.0 Final | **Data**: Outubro 2025 | **Status**:  Produção

 **Sistema 100% Operacional!** 
