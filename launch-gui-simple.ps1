#!/usr/bin/env powershell

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "  UTC Weather Reports - Interface Grafica" -ForegroundColor Cyan
Write-Host "  Iniciando Aplicacao..." -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan

$projectDir = "c:\Users\Irving Samuel\Documents\Projeto IA\Banco de dados"

if (!(Test-Path $projectDir)) {
    Write-Host "ERRO - Diretorio nao encontrado!" -ForegroundColor Red
    exit 1
}

Set-Location $projectDir

# Verificar se venv existe
if (!(Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "OK - Ambiente virtual criado`n" -ForegroundColor Green
}

# Ativar venv
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "OK - Ambiente ativo`n" -ForegroundColor Green

# Verificar PyQt5
Write-Host "Verificando dependencias..." -ForegroundColor Yellow

python -c "import PyQt5" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  - Instalando PyQt5..." -ForegroundColor Cyan
    pip install "PyQt5==5.15.10" -q
}

python -c "import psycopg2" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  - Instalando psycopg2..." -ForegroundColor Cyan
    pip install "psycopg2-binary==2.9.11" -q
}

python -c "import jinja2" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  - Instalando Jinja2..." -ForegroundColor Cyan
    pip install "Jinja2==3.1.2" -q
}

python -c "import apscheduler" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  - Instalando APScheduler..." -ForegroundColor Cyan
    pip install "APScheduler==3.10.4" -q
}

Write-Host "OK - Todas as dependencias prontas!`n" -ForegroundColor Green

Write-Host "Iniciando interface grafica...`n" -ForegroundColor Cyan

python -m src.gui

Write-Host "`nAplicacao finalizada!" -ForegroundColor Green
