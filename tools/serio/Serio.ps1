#Requires -Version 5.1
<#
.SYNOPSIS
    Start, stop, restart, and check status of any SERIO or SERIO+ service.

.DESCRIPTION
    One tool for everything:

      serio start data          Start all SERIO+ data services + gateway
      serio start business      Start all SERIO+ business services
      serio start app           Start SERIO+ Angular UI (:4201)
      serio start all           Start full SERIO+ stack (data -> business -> UI)
      serio start monolith      Start SERIO monolith (WebLogic + EAR + Angular :4200)
      serio start <name>        Start a single named service (e.g. serioplus-document-service)

      serio stop data|business|app|all|monolith|<name>
      serio restart <same args as start>

      serio status              Show all running services + port health
      serio build <target>      Build common-lib | data | business | app | all

.EXAMPLE
    serio start all
    serio start monolith
    serio start serioplus-document-service
    serio stop all
    serio restart business
    serio status
    serio build all

.NOTES
    Install as a shell function by dot-sourcing this file in your PowerShell profile:
        . C:\projects\aitools\tools\serio\Serio.ps1

    Or run directly:
        C:\projects\aitools\tools\serio\Serio.ps1 start all
#>

param(
    [string] $Command,
    [string] $Target
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

# ── Paths ─────────────────────────────────────────────────────────────────────
$ROOT        = 'C:\projects'
$DATA_REPO   = "$ROOT\SERIOPlusDataServices"
$SVC_REPO    = "$ROOT\SERIOPlusServices"
$APP_REPO    = "$ROOT\SERIOPlusApp"
$LIB_REPO    = "$ROOT\SERIOPlusCommonLibraries\serioplus-common-library"
$SERIO_REPO  = "$ROOT\SERIO"
$SERIO_APP   = "$ROOT\SERIO\serio-app-war"
$WL_START    = 'C:\FDA\AppServer\Oracle_Home_14120\user_projects\domains\serio\bin\startWebLogic.cmd'
$STATE_DIR   = "$ROOT\.serio-stack"
$STATE_FILE  = "$STATE_DIR\state.json"
$JDK17       = 'C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$JDK21       = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot'

# ── Service definitions ────────────────────────────────────────────────────────
$DATA_SERVICES = [ordered]@{
    'serioplus-entry-data-service'    = @{ repo=$DATA_REPO; port=8090 }
    'serioplus-lookup-data-service'   = @{ repo=$DATA_REPO; port=8091 }
    'serioplus-user-org-data-service' = @{ repo=$DATA_REPO; port=8092 }
    'serioplus-work-data-service'     = @{ repo=$DATA_REPO; port=8093 }
    'serioplus-application-service'   = @{ repo=$DATA_REPO; port=8094 }
    'serioplus-document-service'      = @{ repo=$DATA_REPO; port=8095 }
    'serioplus-screening-data-service'= @{ repo=$DATA_REPO; port=8096 }
    'serioplus-filer-eval-data-service'=@{ repo=$DATA_REPO; port=8097 }
    'local-gateway-service'           = @{ repo=$DATA_REPO; port=8070 }  # gateway last
}

$BIZ_SERVICES = [ordered]@{
    'serioplus-general-admin-service' = @{ repo=$SVC_REPO; port=8080 }
    'serioplus-user-option-service'   = @{ repo=$SVC_REPO; port=8081 }
    'serioplus-aiml-services'         = @{ repo=$SVC_REPO; port=8082 }
    'serioplus-workflow-service'      = @{ repo=$SVC_REPO; port=8083 }
    'serioplus-notice-service'        = @{ repo=$SVC_REPO; port=8084 }
    'serioplus-screening-service'     = @{ repo=$SVC_REPO; port=8085 }
    'serioplus-filer-eval-service'    = @{ repo=$SVC_REPO; port=8086 }
}

$ALL_SERVICES = [ordered]@{}
foreach ($k in $DATA_SERVICES.Keys) { $ALL_SERVICES[$k] = $DATA_SERVICES[$k] }
foreach ($k in $BIZ_SERVICES.Keys)  { $ALL_SERVICES[$k] = $BIZ_SERVICES[$k] }

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Step  { param($m) Write-Host "`n▶ $m" -ForegroundColor Cyan }
function Write-Ok    { param($m) Write-Host "  ✓ $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "  ⚠ $m" -ForegroundColor Yellow }
function Write-Fail  { param($m) Write-Host "  ✗ $m" -ForegroundColor Red }
function Write-Info  { param($m) Write-Host "  $m" -ForegroundColor DarkGray }

function Use-Jdk { param($v)
    $jdk = if ($v -eq 17) { $JDK17 } else { $JDK21 }
    if (-not (Test-Path "$jdk\bin\java.exe")) {
        # Try to auto-discover
        $jdk = Get-ChildItem 'C:\Program Files\Eclipse Adoptium' -Directory -EA 0 |
               Where-Object { $_.Name -match "jdk-$v" -and (Test-Path "$($_.FullName)\bin\java.exe") } |
               Select-Object -First 1 | ForEach-Object { $_.FullName }
        if (-not $jdk) { Write-Fail "JDK $v not found. Install Eclipse Adoptium JDK $v."; return $false }
    }
    $env:JAVA_HOME = $jdk
    $env:PATH = "$jdk\bin;$env:PATH"
    Write-Info "JDK $v: $jdk"
    return $true
}

function Port-Up { param([int]$p)
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$p); $c.Close(); return $true } catch { return $false }
}

function Wait-For-Port { param([int]$p, [string]$label, [int]$sec=120)
    Write-Host "  Waiting for $label on :$p" -NoNewline -ForegroundColor DarkGray
    $deadline = (Get-Date).AddSeconds($sec)
    while ((Get-Date) -lt $deadline) {
        if (Port-Up $p) { Write-Host " UP" -ForegroundColor Green; return $true }
        Write-Host "." -NoNewline -ForegroundColor DarkGray; Start-Sleep 3
    }
    Write-Host " TIMEOUT" -ForegroundColor Red; return $false
}

function Find-Jar { param($name, $repo)
    Get-ChildItem "$repo\$name\target" -Filter "$name*.jar" -EA 0 |
        Where-Object { $_.Name -notmatch '\.(original|sources|javadoc)\.jar$' } |
        Select-Object -First 1
}

function Load-State { if (Test-Path $STATE_FILE) { Get-Content $STATE_FILE -Raw | ConvertFrom-Json } else { @() } }
function Save-State { param($s)
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    ($s | ConvertTo-Json -Depth 5) | Set-Content $STATE_FILE -Encoding utf8
}

function Add-State { param($name, $pid, $port, $tier, $log)
    $state = [System.Collections.Generic.List[object]]::new()
    foreach ($e in @(Load-State)) { if ($e.Name -ne $name) { $state.Add($e) } }
    $state.Add([pscustomobject]@{ Name=$name; Pid=$pid; Port=$port; Tier=$tier; Log=$log })
    Save-State $state
}

function Remove-From-State { param($name)
    $state = @(Load-State) | Where-Object { $_.Name -ne $name }
    Save-State $state
}

# ── Start a single Spring Boot jar ────────────────────────────────────────────
function Start-SpringService { param($name, $def)
    if (Port-Up $def.port) { Write-Warn "$name already up on :$($def.port)"; return }
    $jar = Find-Jar $name $def.repo
    if (-not $jar) { Write-Fail "$name: jar not found — run: serio build data (or business)"; return }
    $log = "$STATE_DIR\$name.log"
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    $p = Start-Process java `
        -ArgumentList @('-Dspring.profiles.active=local', '-jar', "`"$($jar.FullName)`"") `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err" `
        -PassThru -WindowStyle Hidden
    Add-State $name $p.Id $def.port 'serioplus' $log
    Write-Ok "$name (PID $($p.Id)) :$($def.port)"
}

# ── Stop by name ──────────────────────────────────────────────────────────────
function Stop-Named { param($name)
    # Check state file first
    $entry = @(Load-State) | Where-Object { $_.Name -eq $name } | Select-Object -First 1
    if ($entry) {
        try { Stop-Process -Id $entry.Pid -Force -EA Stop; Write-Ok "stopped $name (PID $($entry.Pid))" }
        catch { Write-Warn "$name PID $($entry.Pid) not running" }
        Remove-From-State $name
        return
    }
    # Fallback: kill by cmdline
    $procs = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -EA 0 |
             Where-Object { $_.CommandLine -like "*$name*" }
    if ($procs) {
        $procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA 0; Write-Ok "stopped $name (PID $($_.ProcessId))" }
    } else {
        Write-Warn "$name: not found running"
    }
}

# ── COMMANDS ──────────────────────────────────────────────────────────────────
function Invoke-Start { param($t)
    switch -Wildcard ($t) {
        'all' {
            Write-Step "Starting full SERIO+ stack"
            if (-not (Use-Jdk 17)) { return }
            Write-Step "Data layer"
            foreach ($n in $DATA_SERVICES.Keys) { Start-SpringService $n $DATA_SERVICES[$n] }
            Wait-For-Port 8070 'gateway' 120 | Out-Null
            Write-Step "Business layer"
            foreach ($n in $BIZ_SERVICES.Keys) { Start-SpringService $n $BIZ_SERVICES[$n] }
            Start-Sleep 3
            Write-Step "Angular UI"
            Start-NgServe
            Write-Ok "Stack started → http://localhost:4201/serioplus/#/?acceptBanner=true"
        }
        'data' {
            Write-Step "Starting data layer"
            if (-not (Use-Jdk 17)) { return }
            foreach ($n in $DATA_SERVICES.Keys) { Start-SpringService $n $DATA_SERVICES[$n] }
            Wait-For-Port 8070 'gateway' 120 | Out-Null
        }
        'business' {
            Write-Step "Starting business layer"
            if (-not (Use-Jdk 17)) { return }
            if (-not (Port-Up 8070)) { Write-Warn "Gateway :8070 not up — start data tier first: serio start data" }
            foreach ($n in $BIZ_SERVICES.Keys) { Start-SpringService $n $BIZ_SERVICES[$n] }
        }
        'app' {
            Write-Step "Starting Angular UI"
            Start-NgServe
            Write-Ok "→ http://localhost:4201/serioplus/#/?acceptBanner=true"
        }
        'monolith' {
            Write-Step "Starting SERIO monolith"
            if (-not (Use-Jdk 21)) { return }
            Start-Monolith
        }
        default {
            # Single named service
            $def = $ALL_SERVICES[$t]
            if ($def) {
                if (-not (Use-Jdk 17)) { return }
                Write-Step "Starting $t"
                Start-SpringService $t $def
            } else {
                Write-Fail "Unknown target: '$t'`nValid: all | data | business | app | monolith | <service-name>"
                Show-ServiceList
            }
        }
    }
}

function Invoke-Stop { param($t)
    switch -Wildcard ($t) {
        'all' {
            Write-Step "Stopping SERIO+ stack"
            foreach ($n in $ALL_SERVICES.Keys) { Stop-Named $n }
            Stop-Named 'app-ngserve'
            $state = @(Load-State) | Where-Object { $_.Tier -eq 'serioplus' }
            Remove-Item $STATE_FILE -EA 0
        }
        'data'     { Write-Step "Stopping data layer";     foreach ($n in $DATA_SERVICES.Keys) { Stop-Named $n } }
        'business' { Write-Step "Stopping business layer"; foreach ($n in $BIZ_SERVICES.Keys)  { Stop-Named $n } }
        'app'      { Write-Step "Stopping Angular UI";     Stop-Named 'app-ngserve' }
        'monolith' { Write-Step "Stopping SERIO monolith"; Stop-Monolith }
        default    { Write-Step "Stopping $t"; Stop-Named $t }
    }
}

function Invoke-Restart { param($t)
    Write-Step "Restarting $t"
    Invoke-Stop $t
    Start-Sleep 2
    Invoke-Start $t
}

function Invoke-Build { param($t)
    switch ($t) {
        'common-lib' { Build-CommonLib }
        'data'       { Build-CommonLib; Build-Maven $DATA_REPO 'data services' }
        'business'   { Build-Maven $SVC_REPO 'business services' }
        'app'        { Build-App }
        'all'        {
            Build-CommonLib
            Build-Maven $DATA_REPO 'data services'
            Build-Maven $SVC_REPO 'business services'
            Build-App
        }
        default { Write-Fail "Unknown build target: '$t'`nValid: common-lib | data | business | app | all" }
    }
}

function Build-CommonLib {
    Write-Step "Building common-lib (13.0.0-SNAPSHOT)"
    if (-not (Use-Jdk 17)) { return }
    Push-Location $LIB_REPO
    & mvn -DskipTests clean install
    if ($LASTEXITCODE -eq 0) { Write-Ok "common-lib installed" } else { Write-Fail "common-lib build failed" }
    Pop-Location
}

function Build-Maven { param($repo, $label)
    Write-Step "Building $label"
    if (-not (Use-Jdk 17)) { return }
    Push-Location $repo
    & mvn -DskipTests -nsu clean install
    if ($LASTEXITCODE -eq 0) { Write-Ok "$label built" } else { Write-Fail "$label build failed" }
    Pop-Location
}

function Build-App {
    Write-Step "Installing SERIOPlusApp npm deps"
    if (-not (Test-Path "$APP_REPO\.npmrc") -and (Test-Path "$APP_REPO\.npmrc.example")) {
        Copy-Item "$APP_REPO\.npmrc.example" "$APP_REPO\.npmrc"
        Write-Info "Copied .npmrc.example → .npmrc"
    }
    Push-Location $APP_REPO
    & npm install
    if ($LASTEXITCODE -eq 0) { Write-Ok "npm install done" } else { Write-Fail "npm install failed" }
    Pop-Location
}

function Start-NgServe {
    if (Port-Up 4201) { Write-Warn "Angular already up on :4201"; return }
    $log = "$STATE_DIR\app-ngserve.log"
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    $p = Start-Process cmd -ArgumentList '/c', "npm start > `"$log`" 2>&1" `
         -WorkingDirectory $APP_REPO -PassThru -WindowStyle Hidden
    Add-State 'app-ngserve' $p.Id 4201 'serioplus' $log
    Write-Ok "ng serve (PID $($p.Id)) :4201  log: $log"
}

function Start-Monolith {
    if (-not (Test-Path $WL_START)) { Write-Fail "WebLogic not found at $WL_START"; return }

    # WebLogic
    if (Port-Up 7001) {
        Write-Ok "WebLogic already up on :7001"
    } else {
        $wlLog = "$STATE_DIR\weblogic.log"
        New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
        $p = Start-Process cmd -ArgumentList '/c', "`"$WL_START`" > `"$wlLog`" 2>&1" `
             -PassThru -WindowStyle Normal
        Add-State 'weblogic' $p.Id 7001 'monolith' $wlLog
        Write-Ok "WebLogic starting (PID $($p.Id)) — waiting for :7001..."
        if (-not (Wait-For-Port 7001 'WebLogic' 240)) { Write-Fail "WebLogic did not come up. Check: $wlLog"; return }
    }

    # EAR deploy
    Write-Step "Deploying serio-ws.ear"
    Push-Location $SERIO_REPO
    & mvn -DskipTests -Pdeveloper clean package
    if ($LASTEXITCODE -ne 0) { Write-Fail "EAR build/deploy failed"; Pop-Location; return }
    Pop-Location
    Write-Ok "EAR deployed"

    # Angular
    if (Port-Up 4200) {
        Write-Warn "SERIO Angular already up on :4200"
    } else {
        $log = "$STATE_DIR\serio-app.log"
        $p = Start-Process cmd -ArgumentList '/c', "npm start > `"$log`" 2>&1" `
             -WorkingDirectory $SERIO_APP -PassThru -WindowStyle Hidden
        Add-State 'serio-app' $p.Id 4200 'monolith' $log
        Write-Ok "SERIO Angular (PID $($p.Id)) :4200  log: $log"
    }

    Write-Ok "Monolith started → http://localhost:4200"
}

function Stop-Monolith {
    Stop-Named 'weblogic'
    Stop-Named 'serio-app'
    # Also kill any WebLogic java process by cmdline
    Get-CimInstance Win32_Process -Filter "Name='java.exe'" -EA 0 |
        Where-Object { $_.CommandLine -like '*weblogic*' -or $_.CommandLine -like '*startWebLogic*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA 0; Write-Ok "killed WebLogic java (PID $($_.ProcessId))" }
}

function Invoke-Status {
    Write-Host "`n━━ SERIO Stack Status ━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    $allPorts = @(
        @{Port=4200; Label='SERIO Angular (monolith)'}
        @{Port=4201; Label='SERIO+ Angular UI'}
        @{Port=7001; Label='WebLogic'}
        @{Port=8070; Label='gateway'}
        @{Port=8080; Label='general-admin'}
        @{Port=8081; Label='user-option'}
        @{Port=8082; Label='aiml'}
        @{Port=8083; Label='workflow'}
        @{Port=8084; Label='notice'}
        @{Port=8085; Label='screening-svc'}
        @{Port=8086; Label='filer-eval-svc'}
        @{Port=8090; Label='entry-data'}
        @{Port=8091; Label='lookup-data'}
        @{Port=8092; Label='user-org-data'}
        @{Port=8093; Label='work-data'}
        @{Port=8094; Label='application'}
        @{Port=8095; Label='document'}
        @{Port=8096; Label='screening-data'}
        @{Port=8097; Label='filer-eval-data'}
    )

    foreach ($s in $allPorts) {
        $up = Port-Up $s.Port
        $icon  = if ($up) { '●' } else { '○' }
        $color = if ($up) { 'Green' } else { 'DarkGray' }
        Write-Host ("  {0} :{1,-5}  {2}" -f $icon, $s.Port, $s.Label) -ForegroundColor $color
    }

    Write-Host "`n━━ Tracked PIDs ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    $state = @(Load-State)
    if (-not $state) {
        Write-Info "(nothing tracked — processes started manually won't appear here)"
    } else {
        foreach ($e in $state) {
            $alive = $null -ne (Get-Process -Id $e.Pid -EA 0)
            $icon  = if ($alive) { '●' } else { '○' }
            $color = if ($alive) { 'Green' } else { 'DarkGray' }
            Write-Host ("  {0} {1,-45} PID {2}" -f $icon, $e.Name, $e.Pid) -ForegroundColor $color
        }
    }
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
}

function Show-ServiceList {
    Write-Host "`nData services:     $($DATA_SERVICES.Keys -join ', ')"
    Write-Host "Business services: $($BIZ_SERVICES.Keys -join ', ')"
}

function Show-Help {
    Write-Host @"

USAGE:  serio <command> <target>

COMMANDS
  start   <target>    Start services
  stop    <target>    Stop services
  restart <target>    Stop then start
  build   <target>    Build / install (Maven / npm)
  status              Show all ports and tracked PIDs

TARGETS
  all                 Full SERIO+ stack (data → business → UI)
  data                SERIOPlusDataServices (:8090-8097 + gateway :8070)
  business            SERIOPlusServices (:8080-8086)
  app                 SERIOPlusApp Angular UI (:4201)
  monolith            SERIO monolith (WebLogic :7001 + Angular :4200)
  <service-name>      Any single service (e.g. serioplus-document-service)

BUILD TARGETS
  all                 common-lib → data → business → app
  common-lib          serioplus-common-library:13.0.0-SNAPSHOT
  data                SERIOPlusDataServices
  business            SERIOPlusServices
  app                 SERIOPlusApp npm install

EXAMPLES
  serio start all
  serio start monolith
  serio start data
  serio start serioplus-document-service
  serio stop all
  serio restart business
  serio restart serioplus-work-data-service
  serio status
  serio build all

"@ -ForegroundColor White
}

# ── Entry point ───────────────────────────────────────────────────────────────
switch ($Command.ToLower()) {
    'start'   { if ($Target) { Invoke-Start $Target }   else { Show-Help } }
    'stop'    { if ($Target) { Invoke-Stop $Target }    else { Show-Help } }
    'restart' { if ($Target) { Invoke-Restart $Target } else { Show-Help } }
    'build'   { if ($Target) { Invoke-Build $Target }   else { Show-Help } }
    'status'  { Invoke-Status }
    ''        { Show-Help }
    default   { Write-Fail "Unknown command: '$Command'"; Show-Help }
}
