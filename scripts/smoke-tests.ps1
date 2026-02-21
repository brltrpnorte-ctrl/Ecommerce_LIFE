# Smoke tests for Ecommerce_LIFE API (Core + CRM)
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\smoke-tests.ps1
# Requires API running at $BaseUrl

param(
    [string]$BaseUrl = 'http://127.0.0.1:8000/api/v1'
)

$report = [ordered]@{}
$report.timestamp = (Get-Date).ToString('s')
$report.base_url = $BaseUrl
$report.results = @{}

function Resolve-AdminToken {
    $envFile = Join-Path (Split-Path -Parent $PSScriptRoot) 'backend\.env'
    $token = 'change-this-token-in-production'
    if (Test-Path $envFile) {
        $lines = Get-Content $envFile | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '=' }
        foreach ($line in $lines) {
            $parts = $line -split '=', 2
            if ($parts[0].Trim().ToUpper() -eq 'AUTH_TOKEN') {
                $token = $parts[1].Trim()
            }
        }
    }
    return $token
}

function SafeInvoke($name, $scriptblock) {
    try {
        $res = & $scriptblock
        $report.results[$name] = @{ success = $true; response = $res }
        return $res
    } catch {
        $status = $null
        if ($_.Exception.Response) {
            try { $status = [int]$_.Exception.Response.StatusCode } catch { $status = $null }
        }
        $report.results[$name] = @{ success = $false; status = $status; error = $_.Exception.Message }
        return $null
    }
}

function ExpectStatus($name, $scriptblock, [int]$expectedStatus) {
    try {
        & $scriptblock | Out-Null
        if ($expectedStatus -ge 200 -and $expectedStatus -lt 300) {
            $report.results[$name] = @{ success = $true; expected_status = $expectedStatus; actual_status = $expectedStatus }
        } else {
            $report.results[$name] = @{ success = $false; expected_status = $expectedStatus; actual_status = 200; error = 'Expected failure status but request succeeded' }
        }
    } catch {
        $status = $null
        if ($_.Exception.Response) {
            try { $status = [int]$_.Exception.Response.StatusCode } catch { $status = $null }
        }
        $ok = ($status -eq $expectedStatus)
        $report.results[$name] = @{ success = $ok; expected_status = $expectedStatus; actual_status = $status; error = $_.Exception.Message }
    }
}

$adminToken = Resolve-AdminToken

# Core endpoints
SafeInvoke 'health' { Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get } | Out-Null
SafeInvoke 'products' { Invoke-RestMethod -Uri "$BaseUrl/products" -Method Get } | Out-Null
SafeInvoke 'categories' { Invoke-RestMethod -Uri "$BaseUrl/categories" -Method Get } | Out-Null
SafeInvoke 'brands' { Invoke-RestMethod -Uri "$BaseUrl/brands" -Method Get } | Out-Null

ExpectStatus 'admin_invalid_token_401' {
    Invoke-RestMethod -Uri "$BaseUrl/admin/overview" -Headers @{ 'X-Admin-Token' = 'invalid-token' } -Method Get
} 401

SafeInvoke 'admin_valid_token' {
    Invoke-RestMethod -Uri "$BaseUrl/admin/overview" -Headers @{ 'X-Admin-Token' = $adminToken } -Method Get
} | Out-Null

$shipPayload = @{ zip_code = '04129-060'; subtotal = 199.99; weight_kg = 2.4 } | ConvertTo-Json
SafeInvoke 'shipping_quote' { Invoke-RestMethod -Uri "$BaseUrl/shipping/quote" -Method Post -Body $shipPayload -ContentType 'application/json' } | Out-Null

$checkoutPayload = @{ cart_total = 240.5; method = 'cartao'; installments = 3; customer_email = 'validacao@life.com' } | ConvertTo-Json
SafeInvoke 'checkout_validate' { Invoke-RestMethod -Uri "$BaseUrl/checkout/validate" -Method Post -Body $checkoutPayload -ContentType 'application/json' } | Out-Null

# CRM capture (public endpoint)
$leadPayload = @{
    name = 'Lead Smoke'
    email = "lead-smoke-$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())@life.com"
    phone = '11999990000'
    company = 'Life Test'
    job_title = 'Buyer'
    source = 'smoke-test'
    tags = @('smoke', 'qa')
    consent = $true
    owner = 'time-a'
    estimated_value = 950
    close_probability = 35
    notes = 'Lead criado por smoke test'
} | ConvertTo-Json -Depth 4

$captureResponse = SafeInvoke 'crm_capture_lead' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/leads/capture" -Method Post -Body $leadPayload -ContentType 'application/json'
}

$leadId = $null
if ($captureResponse -and $captureResponse.lead) {
    $leadId = [int]$captureResponse.lead.id
}

# CRM access control
ExpectStatus 'crm_dashboard_without_role_403' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/dashboard" -Method Get
} 403

SafeInvoke 'crm_dashboard_vendedor' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/dashboard" -Method Get -Headers @{ 'X-User-Role' = 'vendedor' }
} | Out-Null

SafeInvoke 'crm_contacts_vendedor' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/contacts" -Method Get -Headers @{ 'X-User-Role' = 'vendedor' }
} | Out-Null

SafeInvoke 'crm_leads_vendedor' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/leads" -Method Get -Headers @{ 'X-User-Role' = 'vendedor' }
} | Out-Null

if ($leadId) {
    $leadPatch = @{ stage = 'qualificado'; touchpoint = $true } | ConvertTo-Json
    ExpectStatus 'crm_update_lead_vendedor_forbidden_403' {
        Invoke-RestMethod -Uri "$BaseUrl/crm/leads/$leadId" -Method Patch -Headers @{ 'X-User-Role' = 'vendedor' } -Body $leadPatch -ContentType 'application/json'
    } 403

    SafeInvoke 'crm_update_lead_gerente' {
        Invoke-RestMethod -Uri "$BaseUrl/crm/leads/$leadId" -Method Patch -Headers @{ 'X-User-Role' = 'gerente' } -Body $leadPatch -ContentType 'application/json'
    } | Out-Null

    $taskPayload = @{ lead_id = $leadId; title = 'Follow-up manual smoke'; due_date = (Get-Date).AddDays(2).ToString('s') } | ConvertTo-Json
    SafeInvoke 'crm_create_task_gerente' {
        Invoke-RestMethod -Uri "$BaseUrl/crm/tasks" -Method Post -Headers @{ 'X-User-Role' = 'gerente' } -Body $taskPayload -ContentType 'application/json'
    } | Out-Null
}

SafeInvoke 'crm_followup_automation_gerente' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/automation/follow-ups?stale_days=1" -Method Post -Headers @{ 'X-User-Role' = 'gerente' }
} | Out-Null

SafeInvoke 'crm_audit_admin' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/audit?limit=20" -Method Get -Headers @{ 'X-Admin-Token' = $adminToken }
} | Out-Null

SafeInvoke 'crm_backup_admin' {
    Invoke-RestMethod -Uri "$BaseUrl/crm/backup" -Method Post -Headers @{ 'X-Admin-Token' = $adminToken }
} | Out-Null

# Report
$reportsDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'reports'
if (!(Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }
$outFile = Join-Path $reportsDir "smoke-report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report | ConvertTo-Json -Depth 8 | Set-Content -Path $outFile -Encoding UTF8

Write-Output "Smoke report written to: $outFile"
