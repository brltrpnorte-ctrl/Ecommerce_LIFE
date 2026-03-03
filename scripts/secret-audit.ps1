param(
    [string]$Root = "."
)

$ErrorActionPreference = "Stop"

$patterns = @(
    @{ Name = "Supabase Service Role"; Regex = 'SUPABASE_SERVICE_ROLE_KEY\s*=\s*(?!REPLACE)[A-Za-z0-9_\-]{20,}' },
    @{ Name = "Supabase Publishable/Anon (hardcoded)"; Regex = 'sb_(publishable|anon)_[A-Za-z0-9_\-]+' },
    @{ Name = "Postgres URL with password"; Regex = 'postgres(?:ql)?://[^:\s]+:[^@\s]+@' },
    @{ Name = "Admin Token assignment"; Regex = 'AUTH_TOKEN\s*=\s*(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*\d)[A-Za-z0-9_-]{20,}' },
    @{ Name = "Admin Token literal in docs/scripts"; Regex = '(?i)(auth[_\s-]?token|admin token|x-admin-token)[^`\"\''\r\n]{0,40}[`\"\''=:]\s*(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*\d)[A-Za-z0-9_-]{20,}' },
    @{ Name = "JWT-like token assignment"; Regex = '(?i)(service_role_key|oidc_token)\s*=\s*\"?eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\"?' }
)

$includeFiles = Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch "\\node_modules\\" -and
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\.git\\" -and
        $_.FullName -notmatch "\\__pycache__\\" -and
        $_.FullName -notmatch "\\dist\\" -and
        $_.FullName -notmatch "\\.vercel\\" -and
        $_.Name -notmatch "^\.env$" -and
        $_.Name -notmatch "^\.env(\..+)?\.local$" -and
        $_.Name -notmatch "\.db$|\.png$|\.jpg$|\.jpeg$|\.gif$|\.mp4$|\.zip$|\.pdf$"
    }

$findings = @()

foreach ($pattern in $patterns) {
    $matches = $includeFiles | Select-String -Pattern $pattern.Regex -AllMatches -ErrorAction SilentlyContinue
    foreach ($m in $matches) {
        if ($m.Path -match "scripts\\secret-audit\.ps1$") { continue }
        if ($m.Line -match "REPLACE_WITH|YOUR_PROJECT|YOUR_POOLER_HOST|YOUR_BACKEND_PROJECT|<ADMIN_TOKEN>|<SEU_TOKEN|<SEU_AUTH_TOKEN|<GERAR_TOKEN_FORTE|GERE_UM_TOKEN_FORTE|GERE_TOKEN_FORTE|change-this-token-in-production|SUA_CHAVE_SERVICE_ROLE|SEU_REF|<PROJECT_REF>|<POOLER_HOST>|<PASSWORD>@|user:password@|localhost/ecommerce_life|ecommerce_user:ecommerce_secure_password@") { continue }
        $findings += [PSCustomObject]@{
            Type = $pattern.Name
            File = $m.Path
            Line = $m.LineNumber
            Text = $m.Line.Trim()
        }
    }
}

if ($findings.Count -eq 0) {
    Write-Host "OK: Nenhum segredo aparente encontrado pelos padrões configurados."
    exit 0
}

Write-Host "ATENCAO: Possiveis segredos encontrados:" -ForegroundColor Yellow
$findings | Sort-Object File, Line | Format-Table -AutoSize
exit 1
