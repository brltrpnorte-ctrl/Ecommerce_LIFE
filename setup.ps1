# Setup completo do Ecommerce LIFE
Write-Host "=== Ecommerce LIFE - Setup ===" -ForegroundColor Green

# 1. Gerar token seguro
Write-Host "`n[1/3] Gerando token seguro..." -ForegroundColor Cyan
$token = python backend/generate_token.py 2>&1 | Select-String -Pattern "^[A-Za-z0-9_-]{43}$" | Select-Object -First 1
if ($token) {
    Write-Host "Token gerado: $token" -ForegroundColor Yellow
    
    # 2. Atualizar .env
    Write-Host "`n[2/3] Atualizando backend/.env..." -ForegroundColor Cyan
    $envPath = "backend/.env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath
        $content = $content -replace "AUTH_TOKEN=.*", "AUTH_TOKEN=$token"
        $content | Set-Content $envPath
        Write-Host ".env atualizado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Arquivo .env nao encontrado. Criando..." -ForegroundColor Yellow
        Copy-Item "backend/.env.example" $envPath
        $content = Get-Content $envPath
        $content = $content -replace "AUTH_TOKEN=.*", "AUTH_TOKEN=$token"
        $content | Set-Content $envPath
    }
} else {
    Write-Host "Erro ao gerar token" -ForegroundColor Red
    exit 1
}

# 3. Validar instalacao
Write-Host "`n[3/3] Validando instalacao..." -ForegroundColor Cyan
Write-Host "Backend: " -NoNewline
if (Test-Path "backend/requirements.txt") {
    Write-Host "OK" -ForegroundColor Green
} else {
    Write-Host "FALTANDO" -ForegroundColor Red
}

Write-Host "Frontend: " -NoNewline
if (Test-Path "frontend/package.json") {
    Write-Host "OK" -ForegroundColor Green
} else {
    Write-Host "FALTANDO" -ForegroundColor Red
}

Write-Host "`n=== Setup Concluido ===" -ForegroundColor Green
Write-Host "`nProximos passos:" -ForegroundColor Cyan
Write-Host "1. Backend: cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload"
Write-Host "2. Frontend: cd frontend && npm install && npm run dev"
Write-Host "3. Smoke tests: cd scripts && ./smoke-tests.ps1"
