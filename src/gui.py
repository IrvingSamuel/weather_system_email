"""
Interface Gráfica PyQt5 - UTC Weather Reports (Dark Mode)
"""

import sys
import logging
import os
from datetime import datetime, date
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QDialog, QMessageBox, QProgressBar,
    QTabWidget, QLineEdit, QFormLayout, QDateEdit, QTimeEdit, QCheckBox,
    QFileDialog, QSplitter, QStatusBar, QMenuBar, QMenu, QAction, QToolBar,
    QSizePolicy, QListWidget, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime, QDate, QTime
from PyQt5.QtGui import QIcon, QFont, QColor, QTextCursor, QDesktopServices
from PyQt5.QtCore import QUrl
import psycopg2

from src.database import DatabaseConnection, UTCRepository, WeatherRepository, EventLogRepository
from src.report_generator import ReportGenerator
from src.email_sender import EmailSender
from src.weather_api import WeatherAPIClient, get_location_for_utc
from config.config import RECIPIENTS, SELECTED_UTCS, WEATHER_API_CONFIG, DB_CONFIG, REPORTS_DIR

# Verificar se email esta desabilitado
try:
    from config.config import EMAIL_DISABLED
except ImportError:
    EMAIL_DISABLED = False

logger = logging.getLogger(__name__)


class Worker(QThread):
    """Thread para operações de longa duração"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    report_path = pyqtSignal(str)  # Novo sinal para caminho do relatório
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        try:
            if self.operation == "generate_report":
                self._generate_report()
            elif self.operation == "send_email":
                self._send_email()
            elif self.operation == "update_weather":
                self._update_weather()
            elif self.operation == "fetch_utcs":
                self._fetch_utcs()
            self.finished.emit(True, "Operação concluída com sucesso!")
        except Exception as e:
            logger.error(f"Erro na operação {self.operation}: {e}")
            self.finished.emit(False, f"Erro: {str(e)}")
    
    def _generate_report(self):
        """Gera relatório completo com AUTO-ATUALIZAÇÃO da API"""
        self.progress.emit("🌐 Buscando dados ATUAIS da WeatherAPI.com...")
        
        # PASSO 1: Atualizar dados da API
        api_client = WeatherAPIClient(WEATHER_API_CONFIG['api_key'])
        
        db = DatabaseConnection()
        if not db.connect():
            raise Exception("Falha ao conectar ao banco de dados")
        
        try:
            # Buscar UTCs
            self.progress.emit("📍 Buscando UTCs cadastradas...")
            utc_repo = UTCRepository(db)
            utcs = utc_repo.get_all_utcs()
            
            if not utcs:
                raise Exception("Nenhuma UTC encontrada no banco")
            
            self.progress.emit(f"✅ Encontradas {len(utcs)} UTCs")
            
            # Conectar diretamente para atualizar dados
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Limpar dados antigos
            cur.execute("DELETE FROM weather_predictions")
            conn.commit()
            
            self.progress.emit("🔄 Buscando clima ATUAL de cada UTC...")
            
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
                        weather_data['weather_condition'],  # Já traduzido
                        weather_data['humidity'],
                        weather_data['wind_speed'],
                        climate_type
                    ))
                    
                    conn.commit()
                    self.progress.emit(f"  ✓ {utc_name:8} - {weather_data['temperature']:5.1f}°C - {weather_data['weather_condition']}")
            
            cur.close()
            conn.close()
            
            self.progress.emit("✅ Dados de clima atualizados da API")
            
            # PASSO 2: Buscar dados atualizados do banco
            self.progress.emit("📊 Preparando dados para relatório...")
            weather_repo = WeatherRepository(db)
            report_data = []
            
            for utc in utcs:
                latest = weather_repo.get_latest_weather(utc.get('utc_id'))
                
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
            
            if not report_data:
                raise Exception("Nenhum dado disponível para gerar relatório")
            
            self.progress.emit(f"✅ Dados coletados para {len(report_data)} UTCs")
            
            # PASSO 3: Gerar relatório HTML
            self.progress.emit("📝 Gerando relatório HTML...")
            generator = ReportGenerator()
            filepath = generator.generate_daily_report(report_data)
            
            if not filepath:
                raise Exception("Falha ao gerar arquivo HTML do relatório")
            
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(filepath)
            filename = os.path.basename(filepath)
            
            self.progress.emit(f"✅ Relatório gerado: {filename}")
            self.progress.emit(f"   Tamanho: {file_size:,} bytes")
            
            # Emitir caminho do relatório
            self.report_path.emit(filepath)
            
        finally:
            db.disconnect()
    
    def _send_email(self):
        """Envia email com relatório em anexo"""
        self.progress.emit("📧 Preparando envio de email...")
        
        # Verificar se existe relatório recente
        if not os.path.exists(REPORTS_DIR):
            raise Exception("Pasta de relatórios não encontrada")
        
        # Buscar último relatório gerado
        reports = []
        for file in os.listdir(REPORTS_DIR):
            if file.endswith('.html') and file.startswith('relatorio_utc_'):
                filepath = os.path.join(REPORTS_DIR, file)
                mtime = os.path.getmtime(filepath)
                reports.append((filepath, mtime))
        
        if not reports:
            raise Exception("Nenhum relatório encontrado. Gere um relatório primeiro!")
        
        # Ordenar por data e pegar o mais recente
        reports.sort(key=lambda x: x[1], reverse=True)
        latest_report = reports[0][0]
        report_filename = os.path.basename(latest_report)
        
        self.progress.emit(f"📄 Relatório: {report_filename}")
        
        # Preparar dados para o corpo do email
        db = DatabaseConnection()
        if not db.connect():
            raise Exception("Falha ao conectar ao banco de dados")
        
        try:
            # Buscar UTCs e clima
            utc_repo = UTCRepository(db)
            weather_repo = WeatherRepository(db)
            utcs = utc_repo.get_all_utcs()
            
            utcs_data = []
            for utc in utcs:
                latest = weather_repo.get_latest_weather(utc.get('utc_id'))
                
                utc_info = {
                    'city_name': utc.get('city_name'),
                    'country': utc.get('country'),
                    'description': utc.get('description'),
                    'utc_offset': utc.get('utc_offset'),
                    'utc_name': utc.get('utc_name'),
                    'image_url': utc.get('image_url'),
                    'video_url': utc.get('video_url')
                }
                
                if latest:
                    utc_info.update({
                        'temperature': latest.get('temperature'),
                        'weather_condition': latest.get('weather_condition'),
                        'humidity': latest.get('humidity'),
                        'wind_speed': latest.get('wind_speed'),
                        'climate_type': latest.get('climate_type')
                    })
                
                utcs_data.append(utc_info)
            
            # Criar corpo do email
            from src.email_sender import EmailSender
            email_sender = EmailSender()
            
            self.progress.emit("✍️ Criando corpo do email...")
            html_body = email_sender.create_html_email_body(utcs_data)
            
            # Enviar email
            self.progress.emit(f"📤 Enviando para {len(RECIPIENTS)} destinatário(s)...")
            
            subject = f"Relatório de Previsão do Tempo - UTC Weather Reports - {datetime.now().strftime('%d/%m/%Y')}"
            
            result = email_sender.send_report_email(
                recipients=RECIPIENTS,
                subject=subject,
                html_body=html_body,
                report_file_path=latest_report
            )
            
            if not result['success']:
                raise Exception(result['message'])
            
            self.progress.emit(f"✅ Email enviado com sucesso para {len(RECIPIENTS)} destinatário(s)!")
            
        finally:
            db.disconnect()
    
    def _update_weather(self):
        self.progress.emit("Atualizando dados de previsão...")
        db = DatabaseConnection()
        if db.connect():
            self.progress.emit("Sincronizando com banco de dados...")
            db.disconnect()
    
    def _fetch_utcs(self):
        self.progress.emit("Buscando UTCs...")
        db = DatabaseConnection()
        if db.connect():
            utc_repo = UTCRepository(db)
            utcs = utc_repo.get_all_utcs()
            db.disconnect()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.last_report_path = None  # Armazenar último relatório gerado
        self.setWindowTitle("UTC Weather Reports - Sistema de Gestão (Dark Mode)")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        self.init_ui()
        self.apply_styles()
        
        logger.info("Interface gráfica inicializada (Dark Mode)")
    
    def init_ui(self):
        """Inicializar interface"""
        # Menu Bar
        self.create_menu_bar()
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = self.create_toolbar()
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        tabs.addTab(self.create_utcs_tab(), "📍 UTCs")
        tabs.addTab(self.create_weather_tab(), "🌤️ Previsão")
        tabs.addTab(self.create_reports_tab(), "📄 Relatórios")
        tabs.addTab(self.create_email_tab(), "📧 Email")
        tabs.addTab(self.create_logs_tab(), "📋 Logs")
        tabs.addTab(self.create_settings_tab(), "⚙️ Configurações")
        
        layout.addWidget(tabs)
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Pronto")
    
    def create_menu_bar(self):
        """Criar menu bar"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Operações
        ops_menu = menubar.addMenu("Operações")
        gen_report = QAction("Gerar Relatório", self)
        gen_report.triggered.connect(self.generate_report)
        ops_menu.addAction(gen_report)
        
        send_email = QAction("Enviar Email", self)
        send_email.triggered.connect(self.send_email)
        ops_menu.addAction(send_email)
        
        update_weather = QAction("Atualizar Previsão", self)
        update_weather.triggered.connect(self.update_weather)
        ops_menu.addAction(update_weather)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("Ajuda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Criar toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        gen_btn = QPushButton("📊 Gerar Relatório")
        gen_btn.clicked.connect(self.generate_report)
        toolbar.addWidget(gen_btn)
        
        email_btn = QPushButton("📧 Enviar Email")
        email_btn.clicked.connect(self.send_email)
        toolbar.addWidget(email_btn)
        
        update_btn = QPushButton("🔄 Atualizar Dados")
        update_btn.clicked.connect(self.update_weather)
        toolbar.addWidget(update_btn)
        
        refresh_btn = QPushButton("🔃 Atualizar Tela")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        toolbar.addWidget(refresh_btn)
        
        return toolbar
    
    def create_dashboard_tab(self):
        """Criar aba Dashboard"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("📊 Dashboard - UTC Weather Reports")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Informações do sistema
        info_layout = QHBoxLayout()
        
        # Card 1: Status BD
        status_label = QLabel()
        if self.db.connect():
            status_label.setText("✅ Banco: Conectado")
            status_label.setStyleSheet("background-color: #d4edda; padding: 10px; border-radius: 5px;")
            self.db.disconnect()
        else:
            status_label.setText("❌ Banco: Desconectado")
            status_label.setStyleSheet("background-color: #f8d7da; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(status_label)
        
        # Card 2: Hora
        time_label = QLabel(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        time_label.setStyleSheet("background-color: #cfe2ff; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(time_label)
        
        # Card 3: Total de UTCs
        utc_label = QLabel("📍 UTCs: Carregando...")
        utc_label.setStyleSheet("background-color: #e2e3e5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(utc_label)
        
        layout.addLayout(info_layout)
        
        # Tabela de UTCs
        layout.addWidget(QLabel("📍 UTCs Cadastradas:"))
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "Nome", "Cidade", "País"])
        table.setRowCount(len(SELECTED_UTCS))
        
        for row, utc in enumerate(SELECTED_UTCS):
            table.setItem(row, 0, QTableWidgetItem(str(utc['utc_id'])))
            table.setItem(row, 1, QTableWidgetItem(utc['utc_name']))
            table.setItem(row, 2, QTableWidgetItem(utc['city']))
            table.setItem(row, 3, QTableWidgetItem(utc['country']))
        
        layout.addWidget(table)
        
        # Log de atividades
        layout.addWidget(QLabel("📋 Log de Atividades:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        gen_btn = QPushButton("📊 Gerar Relatório")
        gen_btn.clicked.connect(self.generate_report)
        btn_layout.addWidget(gen_btn)
        
        email_btn = QPushButton("📧 Enviar Email")
        email_btn.clicked.connect(self.send_email)
        btn_layout.addWidget(email_btn)
        
        refresh_btn = QPushButton("🔄 Atualizar Previsão")
        refresh_btn.clicked.connect(self.update_weather)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_utcs_tab(self):
        """Criar aba UTCs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("📍 Gerenciar UTCs"))
        
        # Tabela
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Nome", "Cidade", "País", "Descrição"])
        table.setRowCount(len(SELECTED_UTCS))
        
        for row, utc in enumerate(SELECTED_UTCS):
            table.setItem(row, 0, QTableWidgetItem(str(utc['utc_id'])))
            table.setItem(row, 1, QTableWidgetItem(utc['utc_name']))
            table.setItem(row, 2, QTableWidgetItem(utc['city']))
            table.setItem(row, 3, QTableWidgetItem(utc['country']))
            table.setItem(row, 4, QTableWidgetItem(utc['description']))
        
        layout.addWidget(table)
        
        # Botões
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Adicionar UTC")
        edit_btn = QPushButton("✏️ Editar")
        delete_btn = QPushButton("🗑️ Deletar")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_weather_tab(self):
        """Criar aba Previsão"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("🌤️ Previsão de Tempo"))
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        utc_combo = QComboBox()
        for utc in SELECTED_UTCS:
            utc_combo.addItem(f"{utc['city']} ({utc['utc_name']})")
        filter_layout.addWidget(QLabel("Selecione UTC:"))
        filter_layout.addWidget(utc_combo)
        
        layout.addLayout(filter_layout)
        
        # Tabela de previsão
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Data", "Temperatura", "Condição", "Umidade", "Vento", "Clima", "Ações"
        ])
        layout.addWidget(table)
        
        return widget
    
    def create_reports_tab(self):
        """Criar aba Relatórios"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("📄 Geração e Visualização de Relatórios")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Grupo: Gerar Novo Relatório
        gen_group = QGroupBox("🆕 Gerar Novo Relatório")
        gen_layout = QVBoxLayout()
        
        info_label = QLabel("✨ O relatório será gerado com dados ATUAIS da WeatherAPI.com em Português")
        info_label.setStyleSheet("color: #0d6efd; font-style: italic; padding: 10px;")
        gen_layout.addWidget(info_label)
        
        # Progresso
        self.report_progress = QProgressBar()
        self.report_progress.setVisible(False)
        gen_layout.addWidget(self.report_progress)
        
        # Botão Gerar
        gen_btn = QPushButton("📊 Gerar Relatório com Dados Atuais")
        gen_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                font-size: 14px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        gen_btn.clicked.connect(self.generate_report)
        gen_layout.addWidget(gen_btn)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Grupo: Relatórios Gerados
        list_group = QGroupBox("📁 Relatórios Gerados")
        list_layout = QVBoxLayout()
        
        # Lista de relatórios
        self.reports_list = QListWidget()
        self.reports_list.itemDoubleClicked.connect(self.open_report_from_list)
        list_layout.addWidget(self.reports_list)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("� Atualizar Lista")
        refresh_btn.clicked.connect(self.refresh_reports_list)
        btn_layout.addWidget(refresh_btn)
        
        open_btn = QPushButton("👁️ Abrir Selecionado")
        open_btn.clicked.connect(self.open_selected_report)
        btn_layout.addWidget(open_btn)
        
        open_latest_btn = QPushButton("🌟 Abrir Último Gerado")
        open_latest_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
            }
        """)
        open_latest_btn.clicked.connect(self.open_latest_report)
        btn_layout.addWidget(open_latest_btn)
        
        open_folder_btn = QPushButton("� Abrir Pasta")
        open_folder_btn.clicked.connect(self.open_reports_folder)
        btn_layout.addWidget(open_folder_btn)
        
        list_layout.addLayout(btn_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Carregar lista inicial
        self.refresh_reports_list()
        
        return widget
    
    def create_email_tab(self):
        """Criar aba Email"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("📧 Envio de Emails"))
        
        # Destinatários
        layout.addWidget(QLabel("Destinatários:"))
        recipients_text = QTextEdit()
        recipients_text.setPlainText("\n".join(RECIPIENTS))
        recipients_text.setMaximumHeight(80)
        layout.addWidget(recipients_text)
        
        # Assunto
        layout.addWidget(QLabel("Assunto:"))
        subject_input = QLineEdit()
        subject_input.setText("Relatório de Previsão do Tempo - UTC Weather Reports")
        layout.addWidget(subject_input)
        
        # Corpo do email
        layout.addWidget(QLabel("Corpo do Email:"))
        body_text = QTextEdit()
        body_text.setPlainText("Segue em anexo o relatório de previsão de tempo...")
        layout.addWidget(body_text)
        
        # Opções
        attach_report = QCheckBox("Anexar relatório HTML")
        attach_report.setChecked(True)
        layout.addWidget(attach_report)
        
        # Progresso
        progress = QProgressBar()
        layout.addWidget(progress)
        
        # Botões
        btn_layout = QHBoxLayout()
        send_btn = QPushButton("📧 Enviar Email")
        send_btn.clicked.connect(self.send_email)
        btn_layout.addWidget(send_btn)
        
        test_btn = QPushButton("🧪 Teste")
        btn_layout.addWidget(test_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return widget
    
    def create_logs_tab(self):
        """Criar aba Logs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("📋 Log de Eventos"))
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        type_combo = QComboBox()
        type_combo.addItems(["Todos", "Inserção", "Atualização", "Deleção", "Email", "Erro"])
        filter_layout.addWidget(QLabel("Tipo:"))
        filter_layout.addWidget(type_combo)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar...")
        filter_layout.addWidget(search_input)
        
        layout.addLayout(filter_layout)
        
        # Tabela de logs
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Tipo", "Tabela", "Ação", "Data/Hora"])
        layout.addWidget(table)
        
        # Botões
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.refresh_logs)
        btn_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Limpar Logs Antigos")
        btn_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("📥 Exportar")
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_settings_tab(self):
        """Criar aba Configurações"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("⚙️ Configurações"))
        
        form_layout = QFormLayout()
        
        # BD
        layout.addWidget(QLabel("Banco de Dados:"))
        bd_form = QFormLayout()
        host = QLineEdit()
        host.setText("localhost")
        bd_form.addRow("Host:", host)
        
        port = QSpinBox()
        port.setValue(5432)
        bd_form.addRow("Porta:", port)
        
        user = QLineEdit()
        user.setText("vscode")
        bd_form.addRow("Usuário:", user)
        
        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)
        bd_form.addRow("Senha:", password)
        
        layout.addLayout(bd_form)
        
        # Email
        layout.addWidget(QLabel("\nEmail:"))
        email_form = QFormLayout()
        
        smtp = QLineEdit()
        smtp.setText("smtp.hostinger.com")
        email_form.addRow("SMTP Server:", smtp)
        
        smtp_port = QSpinBox()
        smtp_port.setValue(465)
        email_form.addRow("SMTP Port:", smtp_port)
        
        email_user = QLineEdit()
        email_user.setText("no-reply@rezum.me")
        email_form.addRow("Email:", email_user)
        
        layout.addLayout(email_form)
        
        # Botões
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Salvar")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🧪 Testar Conexão")
        btn_layout.addWidget(test_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return widget
    
    def generate_report(self):
        """Gerar relatório com auto-atualização da API"""
        self.log_text.append("📊 Iniciando geração de relatório com dados ATUAIS...")
        self.statusBar.showMessage("Gerando relatório...")
        
        # Mostrar progresso
        self.report_progress.setVisible(True)
        self.report_progress.setRange(0, 0)  # Indeterminado
        
        self.worker = Worker("generate_report")
        self.worker.progress.connect(self.log_progress)
        self.worker.finished.connect(self.on_report_generated)
        self.worker.report_path.connect(self.on_report_path_received)
        self.worker.start()
    
    def on_report_path_received(self, filepath):
        """Armazena caminho do último relatório gerado"""
        self.last_report_path = filepath
    
    def on_report_generated(self, success, message):
        """Callback quando relatório é gerado"""
        self.report_progress.setVisible(False)
        
        if success:
            self.log_text.append(f"✅ {message}")
            self.statusBar.showMessage("Relatório gerado com sucesso!")
            
            # Atualizar lista de relatórios
            self.refresh_reports_list()
            
            # Perguntar se quer abrir
            reply = QMessageBox.question(
                self,
                "Relatório Gerado com Sucesso! 🎉",
                f"Relatório gerado com dados ATUAIS em Português!\n\n"
                f"Deseja abrir o relatório agora?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes and hasattr(self, 'last_report_path'):
                self.open_report_file(self.last_report_path)
        else:
            self.log_text.append(f"❌ {message}")
            self.statusBar.showMessage("Erro ao gerar relatório")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório:\n\n{message}")
    
    def refresh_reports_list(self):
        """Atualizar lista de relatórios gerados"""
        self.reports_list.clear()
        
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR, exist_ok=True)
            return
        
        # Buscar todos os arquivos HTML
        reports = []
        for file in os.listdir(REPORTS_DIR):
            if file.endswith('.html') and file.startswith('relatorio_utc_'):
                filepath = os.path.join(REPORTS_DIR, file)
                mtime = os.path.getmtime(filepath)
                size = os.path.getsize(filepath)
                reports.append((file, filepath, mtime, size))
        
        # Ordenar por data de modificação (mais recente primeiro)
        reports.sort(key=lambda x: x[2], reverse=True)
        
        # Adicionar à lista
        for filename, filepath, mtime, size in reports:
            mod_time = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
            size_kb = size / 1024
            item_text = f"📄 {filename}  |  {mod_time}  |  {size_kb:.1f} KB"
            self.reports_list.addItem(item_text)
            # Armazenar caminho completo como dado do item
            self.reports_list.item(self.reports_list.count() - 1).setData(Qt.UserRole, filepath)
        
        # Atualizar contador
        self.log_text.append(f"📁 {len(reports)} relatório(s) encontrado(s)")
    
    def open_selected_report(self):
        """Abrir relatório selecionado"""
        current_item = self.reports_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Nenhum Relatório Selecionado", 
                              "Por favor, selecione um relatório da lista.")
            return
        
        filepath = current_item.data(Qt.UserRole)
        self.open_report_file(filepath)
    
    def open_report_from_list(self, item):
        """Abrir relatório ao dar duplo clique"""
        filepath = item.data(Qt.UserRole)
        self.open_report_file(filepath)
    
    def open_latest_report(self):
        """Abrir último relatório gerado"""
        if self.reports_list.count() == 0:
            QMessageBox.warning(self, "Nenhum Relatório", 
                              "Nenhum relatório foi gerado ainda.\n\n"
                              "Clique em 'Gerar Relatório' para criar um.")
            return
        
        # O primeiro item é o mais recente (lista ordenada)
        latest_item = self.reports_list.item(0)
        filepath = latest_item.data(Qt.UserRole)
        self.open_report_file(filepath)
    
    def open_report_file(self, filepath):
        """Abrir arquivo de relatório no navegador"""
        if not os.path.exists(filepath):
            QMessageBox.critical(self, "Arquivo Não Encontrado", 
                               f"O arquivo não foi encontrado:\n\n{filepath}")
            return
        
        try:
            # Abrir no navegador padrão
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
            self.log_text.append(f"👁️ Abrindo relatório: {os.path.basename(filepath)}")
            self.statusBar.showMessage(f"Abrindo {os.path.basename(filepath)}...")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Abrir", 
                               f"Erro ao abrir relatório:\n\n{str(e)}")
    
    def open_reports_folder(self):
        """Abrir pasta de relatórios no explorador"""
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR, exist_ok=True)
        
        try:
            os.startfile(REPORTS_DIR)
            self.log_text.append(f"📂 Abrindo pasta: {REPORTS_DIR}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pasta:\n\n{str(e)}")
    
    def send_email(self):
        """Enviar email com relatório"""
        # Verificar se email está habilitado
        try:
            from config.config import EMAIL_DISABLED
        except ImportError:
            EMAIL_DISABLED = False
        
        if EMAIL_DISABLED:
            QMessageBox.warning(
                self, 
                "Email Desabilitado", 
                "Envio de email está desabilitado temporariamente.\n\n"
                "Para reabilitar:\n"
                "1. Abra config/config.py\n"
                "2. Configure EMAIL_CONFIG com credenciais válidas\n"
                "3. Defina EMAIL_DISABLED = False"
            )
            return
        
        # Confirmar envio
        reply = QMessageBox.question(
            self,
            "Confirmar Envio de Email",
            f"Deseja enviar o último relatório gerado por email?\n\n"
            f"Destinatários ({len(RECIPIENTS)}):\n" + 
            "\n".join([f"  • {r}" for r in RECIPIENTS]) +
            f"\n\nO email será enviado com o relatório em anexo.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.log_text.append("📧 Iniciando envio de email...")
        self.statusBar.showMessage("Enviando email...")
        
        # Mostrar progresso
        if hasattr(self, 'report_progress'):
            self.report_progress.setVisible(True)
            self.report_progress.setRange(0, 0)
        
        self.worker = Worker("send_email")
        self.worker.progress.connect(self.log_progress)
        self.worker.finished.connect(self.on_email_sent)
        self.worker.start()
    
    def on_email_sent(self, success, message):
        """Callback quando email é enviado"""
        if hasattr(self, 'report_progress'):
            self.report_progress.setVisible(False)
        
        if success:
            self.log_text.append(f"✅ {message}")
            self.statusBar.showMessage("Email enviado com sucesso!")
            
            QMessageBox.information(
                self,
                "Email Enviado! 📧",
                f"Email enviado com sucesso!\n\n"
                f"Destinatários: {len(RECIPIENTS)}\n"
                f"Relatório anexado: último gerado\n\n"
                f"Verifique a caixa de entrada dos destinatários.\n"
                f"(O email pode estar na pasta SPAM)"
            )
        else:
            self.log_text.append(f"❌ {message}")
            self.statusBar.showMessage("Erro ao enviar email")
            QMessageBox.critical(
                self,
                "Erro ao Enviar Email",
                f"Erro ao enviar email:\n\n{message}\n\n"
                f"Verifique:\n"
                f"• Configurações de email em config.py\n"
                f"• Conexão com internet\n"
                f"• Logs do sistema"
            )
    
    def update_weather(self):
        """Atualizar previsão de tempo"""
        self.log_text.append("🔄 Atualizando dados de previsão...")
        self.statusBar.showMessage("Atualizando dados...")
        
        self.worker = Worker("update_weather")
        self.worker.progress.connect(self.log_progress)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.start()
    
    def refresh_dashboard(self):
        """Atualizar dashboard"""
        self.log_text.append("🔃 Atualizando dashboard...")
    
    def refresh_logs(self):
        """Atualizar logs"""
        self.log_text.append("🔄 Atualizando logs...")
    
    def save_settings(self):
        """Salvar configurações"""
        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
    
    def log_progress(self, message):
        """Log de progresso"""
        self.log_text.append(f"⏳ {message}")
        self.log_text.moveCursor(QTextCursor.End)
    
    def on_task_finished(self, success, message):
        """Tarefa finalizada (para outras operações que não sejam relatório)"""
        if success:
            self.log_text.append(f"✅ {message}")
            self.statusBar.showMessage("Pronto")
        else:
            self.log_text.append(f"❌ {message}")
            self.statusBar.showMessage("Erro")
            QMessageBox.critical(
                self,
                "Erro na Operação",
                f"Ocorreu um erro:\n\n{message}\n\nVerifique os logs para mais detalhes."
            )
    
    def show_about(self):
        """Mostrar sobre"""
        QMessageBox.about(
            self,
            "Sobre",
            "UTC Weather Reports v1.0\n\n"
            "Sistema de Gestão de Zonas Horárias e Previsão de Tempo\n\n"
            "Desenvolvido com Python e PyQt5\n\n"
            "© 2025 - Todos os direitos reservados"
        )
    
    def get_stylesheet(self):
        """Retornar stylesheet - MODO ESCURO"""
        return """
        /* MODO ESCURO - Fundo principal */
        QMainWindow, QWidget, QDialog {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        /* Botões - Estilo moderno escuro */
        QPushButton {
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #0b5ed7;
        }
        QPushButton:pressed {
            background-color: #0a58ca;
        }
        QPushButton:disabled {
            background-color: #3d3d3d;
            color: #6c6c6c;
        }
        
        /* Labels - Texto claro */
        QLabel {
            color: #e0e0e0;
            font-size: 13px;
        }
        
        /* Inputs - Fundo escuro */
        QTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            padding: 6px;
            selection-background-color: #0d6efd;
        }
        
        QTextEdit:focus, QLineEdit:focus, QComboBox:focus {
            border: 1px solid #0d6efd;
        }
        
        /* ComboBox - Dropdown */
        QComboBox::drop-down {
            border: none;
            background-color: #3d3d3d;
            border-radius: 3px;
        }
        QComboBox::down-arrow {
            image: none;
            border: 2px solid #e0e0e0;
            width: 6px;
            height: 6px;
            border-top: none;
            border-left: none;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            selection-background-color: #0d6efd;
            border: 1px solid #3d3d3d;
        }
        
        /* Tabelas - Design escuro */
        QTableWidget {
            background-color: #2d2d2d;
            alternate-background-color: #252525;
            gridline-color: #3d3d3d;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
        }
        QTableWidget::item {
            color: #e0e0e0;
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #0d6efd;
        }
        
        /* Cabeçalho da tabela */
        QHeaderView::section {
            background-color: #0d6efd;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        /* Tabs - Abas modernas */
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #1e1e1e;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #a0a0a0;
            border: 1px solid #3d3d3d;
            padding: 10px 25px;
            margin-right: 3px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #0d6efd;
            color: white;
        }
        QTabBar::tab:hover:!selected {
            background-color: #3d3d3d;
            color: #ffffff;
        }
        
        /* Progress Bar */
        QProgressBar {
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            text-align: center;
            color: #e0e0e0;
            height: 25px;
        }
        QProgressBar::chunk {
            background-color: #0d6efd;
            border-radius: 4px;
        }
        
        /* StatusBar */
        QStatusBar {
            background-color: #252525;
            color: #a0a0a0;
            border-top: 1px solid #3d3d3d;
        }
        
        /* MenuBar */
        QMenuBar {
            background-color: #252525;
            color: #e0e0e0;
            border-bottom: 1px solid #3d3d3d;
        }
        QMenuBar::item:selected {
            background-color: #0d6efd;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
        }
        
        /* ToolBar */
        QToolBar {
            background-color: #252525;
            border-bottom: 1px solid #3d3d3d;
            spacing: 5px;
            padding: 5px;
        }
        
        /* ListWidget */
        QListWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
        }
        QListWidget::item:selected {
            background-color: #0d6efd;
        }
        QListWidget::item:hover {
            background-color: #3d3d3d;
        }
        
        /* GroupBox */
        QGroupBox {
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        /* CheckBox */
        QCheckBox {
            color: #e0e0e0;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }
        
        /* ScrollBar */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #5d5d5d;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #7d7d7d;
        }
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #5d5d5d;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }
        """
    
    def apply_styles(self):
        """Aplicar estilos"""
        pass


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
