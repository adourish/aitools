#Requires -Version 5.1
<#
.SYNOPSIS
    Install the 'serio' function into your PowerShell profile so it's available in every terminal.

.EXAMPLE
    C:\projects\aitools\tools\serio\Install-SerioAlias.ps1
#>

$snippet = @'

# ── serio CLI (installed by aitools Install-SerioAlias.ps1) ──────────────────
function serio {
    & 'C:\projects\aitools\tools\serio\Serio.ps1' @args
}
'@

$profile_path = $PROFILE.CurrentUserAllHosts   # works for PowerShell and pwsh

if (-not (Test-Path $profile_path)) {
    New-Item -ItemType File -Path $profile_path -Force | Out-Null
    Write-Host "Created profile: $profile_path" -ForegroundColor Green
}

$existing = Get-Content $profile_path -Raw -EA 0
if ($existing -match 'serio') {
    Write-Host "⚠  'serio' already in profile ($profile_path) — skipping." -ForegroundColor Yellow
    return
}

Add-Content -Path $profile_path -Value $snippet -Encoding utf8
Write-Host "✓ 'serio' function added to $profile_path" -ForegroundColor Green
Write-Host "  Reload with:  . `$PROFILE" -ForegroundColor DarkGray
Write-Host "  Then try:     serio status" -ForegroundColor DarkGray
