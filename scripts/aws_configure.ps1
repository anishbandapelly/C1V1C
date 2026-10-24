# Interactive AWS profile setup for C1V1C. You type the values; they are written only to
# %USERPROFILE%\.aws\credentials and \config (never to the repository). The secret is read as hidden input.
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\aws_configure.ps1 [-Profile c1v1c] [-Region ap-south-2]
param([string]$Profile = 'c1v1c', [string]$Region = 'ap-south-2')
$ErrorActionPreference = 'Stop'

function Set-IniSection([string]$Path, [string]$Section, [hashtable]$Values) {
    $lines = if (Test-Path $Path) { Get-Content $Path } else { @() }
    $out = New-Object System.Collections.Generic.List[string]
    $skip = $false
    foreach ($line in $lines) {
        if ($line -match '^\s*\[(.+)\]\s*$') { $skip = ($Matches[1].Trim() -eq $Section) }
        if (-not $skip) { $out.Add($line) }
    }
    if ($out.Count -and $out[$out.Count - 1].Trim() -ne '') { $out.Add('') }
    $out.Add("[$Section]")
    foreach ($k in $Values.Keys) { $out.Add("$k = $($Values[$k])") }
    Set-Content -Path $Path -Value $out -Encoding Ascii
}

$dir = Join-Path $env:USERPROFILE '.aws'
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$keyId = (Read-Host "AWS Access Key ID (new, rotated key)").Trim()
if ($keyId -notmatch '^(AKIA|ASIA)[A-Z0-9]{12,}$') { throw 'That does not look like an AWS access key ID.' }
$secure = Read-Host "AWS Secret Access Key (hidden)" -AsSecureString
$secret = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
if ($secret.Length -lt 30) { throw 'The secret access key looks too short.' }
$values = [ordered]@{ aws_access_key_id = $keyId; aws_secret_access_key = $secret }
if ($keyId.StartsWith('ASIA')) {
    $token = Read-Host "AWS Session Token (temporary credentials)" -AsSecureString
    $values['aws_session_token'] = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
}

Set-IniSection (Join-Path $dir 'credentials') $Profile $values
Set-IniSection (Join-Path $dir 'config') "profile $Profile" ([ordered]@{ region = $Region; output = 'json' })
$secret = $null
Write-Host "Saved profile '$Profile' (region $Region) to $dir. Tell Claude you're done." -ForegroundColor Green
