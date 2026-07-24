#Requires -Version 5.1
param([string]$Command, [string]$Target)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

# Paths
$ROOT       = 'C:\projects'
$DATA_REPO  = "$ROOT\SERIOPlusDataServices"
$SVC_REPO   = "$ROOT\SERIOPlusServices"
$APP_REPO   = "$ROOT\SERIOPlusApp"
$LIB_REPO   = "$ROOT\SERIOPlusCommonLibraries\serioplus-common-library"
$SERIO_REPO = "$ROOT\SERIO"
$SERIO_APP  = "$ROOT\SERIO\serio-app-war"
$WL_START   = 'C:\FDA\AppServer\Oracle_Home_14120\user_projects\domains\serio\bin\startWebLogic.cmd'
$STATE_DIR  = "$ROOT\.serio-stack"
$STATE_FILE = "$STATE_DIR\state.json"
$JDK17      = 'C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot'
$JDK21      = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot'

# Service definitions
$DATA_SERVICES = [ordered]@{
    'serioplus-entry-data-service'     = @{ repo=$DATA_REPO; port=8090 }
    'serioplus-lookup-data-service'    = @{ repo=$DATA_REPO; port=8091 }
    'serioplus-user-org-data-service'  = @{ repo=$DATA_REPO; port=8092 }
    'serioplus-work-data-service'      = @{ repo=$DATA_REPO; port=8093 }
    'serioplus-application-service'    = @{ repo=$DATA_REPO; port=8094 }
    'serioplus-document-service'       = @{ repo=$DATA_REPO; port=8095 }
    'serioplus-screening-data-service' = @{ repo=$DATA_REPO; port=8096 }
    'serioplus-filer-eval-data-service'= @{ repo=$DATA_REPO; port=8097 }
    'local-gateway-service'            = @{ repo=$DATA_REPO; port=8070 }
}

$BIZ_SERVICES = [ordered]@{
    'serioplus-general-admin-service'  = @{ repo=$SVC_REPO; port=8080 }
    'serioplus-user-option-service'    = @{ repo=$SVC_REPO; port=8081 }
    'serioplus-aiml-services'          = @{ repo=$SVC_REPO; port=8082 }
    'serioplus-workflow-service'       = @{ repo=$SVC_REPO; port=8083 }
    'serioplus-notice-service'         = @{ repo=$SVC_REPO; port=8084 }
    'serioplus-screening-service'      = @{ repo=$SVC_REPO; port=8085 }
    'serioplus-filer-eval-service'     = @{ repo=$SVC_REPO; port=8086 }
}

$ALL_SERVICES = [ordered]@{}
foreach ($k in $DATA_SERVICES.Keys) { $ALL_SERVICES[$k] = $DATA_SERVICES[$k] }
foreach ($k in $BIZ_SERVICES.Keys)  { $ALL_SERVICES[$k] = $BIZ_SERVICES[$k] }

# Output helpers
function Write-Step { param($m) Write-Host "`n>> $m" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "   OK  $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "   WARN $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "   FAIL $m" -ForegroundColor Red }
function Write-Info { param($m) Write-Host "   $m" -ForegroundColor DarkGray }

function Use-Jdk {
    param([int]$v)
    $jdk = if ($v -eq 17) { $JDK17 } else { $JDK21 }
    if (-not (Test-Path "$jdk\bin\java.exe")) {
        $jdk = Get-ChildItem 'C:\Program Files\Eclipse Adoptium' -Directory -EA 0 |
               Where-Object { $_.Name -match "jdk-$v" -and (Test-Path "$($_.FullName)\bin\java.exe") } |
               Select-Object -ExpandProperty FullName -First 1
    }
    if (-not $jdk) { Write-Fail "JDK $v not found. Install Eclipse Adoptium JDK $v."; return $false }
    $env:JAVA_HOME = $jdk
    $env:PATH = "$jdk\bin;" + $env:PATH
    Write-Info "JDK ${v}: $jdk"
    return $true
}

function Port-Up {
    param([int]$p)
    try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', $p); $c.Close(); return $true } catch { return $false }
}

function Wait-For-Port {
    param([int]$p, [string]$label, [int]$sec = 120)
    Write-Host "   Waiting for ${label} on :$p" -NoNewline -ForegroundColor DarkGray
    $deadline = (Get-Date).AddSeconds($sec)
    while ((Get-Date) -lt $deadline) {
        if (Port-Up $p) { Write-Host ' UP' -ForegroundColor Green; return $true }
        Write-Host '.' -NoNewline -ForegroundColor DarkGray
        Start-Sleep 3
    }
    Write-Host ' TIMEOUT' -ForegroundColor Red
    return $false
}

function Find-Jar {
    param($name, $repo)
    Get-ChildItem "$repo\$name\target" -Filter "$name*.jar" -EA 0 |
        Where-Object { $_.Name -notmatch '\.(original|sources|javadoc)\.jar$' } |
        Select-Object -First 1
}

function Load-State {
    if (Test-Path $STATE_FILE) { Get-Content $STATE_FILE -Raw | ConvertFrom-Json } else { @() }
}

function Save-State {
    param($s)
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    ($s | ConvertTo-Json -Depth 5) | Set-Content $STATE_FILE -Encoding utf8
}

function Add-State {
    param($name, $pid, $port, $tier, $log)
    $state = [System.Collections.Generic.List[object]]::new()
    foreach ($e in @(Load-State)) { if ($e.Name -ne $name) { $state.Add($e) } }
    $state.Add([pscustomobject]@{ Name=$name; Pid=$pid; Port=$port; Tier=$tier; Log=$log })
    Save-State $state
}

function Remove-From-State {
    param($name)
    $state = @(Load-State) | Where-Object { $_.Name -ne $name }
    Save-State $state
}

function Start-SpringService {
    param($name, $def)
    if (Port-Up $def.port) { Write-Warn "${name} already up on :$($def.port)"; return }
    $jar = Find-Jar $name $def.repo
    if (-not $jar) {
        Write-Fail "${name}: jar not found -- run: serio build data  (or business)"
        return
    }
    $log = "$STATE_DIR\$name.log"
    $errlog = "$STATE_DIR\$name.err.log"
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    $p = Start-Process java `
        -ArgumentList '-Dspring.profiles.active=local', '-jar', $jar.FullName `
        -RedirectStandardOutput $log `
        -RedirectStandardError  $errlog `
        -PassThru -WindowStyle Hidden
    Add-State $name $p.Id $def.port 'serioplus' $log
    Write-Ok "${name} (PID $($p.Id)) :$($def.port)"
}

function Stop-Named {
    param($name)
    $entry = @(Load-State) | Where-Object { $_.Name -eq $name } | Select-Object -First 1
    if ($entry) {
        try { Stop-Process -Id $entry.Pid -Force -EA Stop; Write-Ok "stopped ${name} (PID $($entry.Pid))" }
        catch { Write-Warn "${name} PID $($entry.Pid) not running" }
        Remove-From-State $name
        return
    }
    $procs = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -EA 0 |
             Where-Object { $_.CommandLine -like "*$name*" }
    if ($procs) {
        $procs | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -EA 0
            Write-Ok "stopped ${name} (PID $($_.ProcessId))"
        }
    } else {
        Write-Warn "${name}: not found running"
    }
}

function Start-NgServe {
    param($repo, $port, $label)
    if (Port-Up $port) { Write-Warn "${label} already up on :${port}"; return }
    $log = "$STATE_DIR\$label.log"
    New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
    $npmArgs = '/c npm start > "' + $log + '" 2>&1'
    $p = Start-Process cmd -ArgumentList $npmArgs -WorkingDirectory $repo -PassThru -WindowStyle Hidden
    Add-State $label $p.Id $port 'serioplus' $log
    Write-Ok "${label} (PID $($p.Id)) :${port}  log: $log"
}

function Start-Monolith {
    if (-not (Test-Path $WL_START)) { Write-Fail "WebLogic not found at $WL_START"; return }
    if (Port-Up 7001) {
        Write-Ok 'WebLogic already up on :7001'
    } else {
        $wlLog = "$STATE_DIR\weblogic.log"
        New-Item -ItemType Directory -Force $STATE_DIR | Out-Null
        $wlArgs = '/c "' + $WL_START + '" > "' + $wlLog + '" 2>&1'
        $p = Start-Process cmd -ArgumentList $wlArgs -PassThru -WindowStyle Normal
        Add-State 'weblogic' $p.Id 7001 'monolith' $wlLog
        Write-Ok "WebLogic starting (PID $($p.Id)) -- waiting for :7001..."
        if (-not (Wait-For-Port 7001 'WebLogic' 240)) {
            Write-Fail "WebLogic timed out. Check $wlLog"
            return
        }
    }
    Write-Step 'Deploying serio-ws.ear'
    Push-Location $SERIO_REPO
    & mvn -DskipTests -Pdeveloper clean package
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -ne 0) { Write-Fail 'EAR build/deploy failed'; return }
    Write-Ok 'EAR deployed'
    Start-NgServe $SERIO_APP 4200 'serio-app'
    Write-Ok 'Monolith started --> http://localhost:4200'
}

function Stop-Monolith {
    Stop-Named 'weblogic'
    Stop-Named 'serio-app'
    Get-CimInstance Win32_Process -Filter "Name='java.exe'" -EA 0 |
        Where-Object { $_.CommandLine -like '*weblogic*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA 0; Write-Ok "killed WebLogic java (PID $($_.ProcessId))" }
}

function Build-CommonLib {
    Write-Step 'Building common-lib (13.0.0-SNAPSHOT)'
    if (-not (Use-Jdk 17)) { return }
    Push-Location $LIB_REPO
    & mvn -DskipTests clean install
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -eq 0) { Write-Ok 'common-lib installed' } else { Write-Fail 'common-lib build failed' }
}

function Build-Maven {
    param($repo, $label)
    Write-Step "Building $label"
    if (-not (Use-Jdk 17)) { return }
    Push-Location $repo
    & mvn -DskipTests -nsu clean install
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -eq 0) { Write-Ok "$label built" } else { Write-Fail "$label build failed" }
}

function Build-App {
    Write-Step 'Installing SERIOPlusApp npm deps'
    if (-not (Test-Path "$APP_REPO\.npmrc") -and (Test-Path "$APP_REPO\.npmrc.example")) {
        Copy-Item "$APP_REPO\.npmrc.example" "$APP_REPO\.npmrc"
        Write-Info 'Copied .npmrc.example -> .npmrc'
    }
    Push-Location $APP_REPO
    & npm install
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -eq 0) { Write-Ok 'npm install done' } else { Write-Fail 'npm install failed' }
}

function Invoke-Start {
    param($t)
    switch ($t) {
        'all' {
            Write-Step 'Starting full SERIO+ stack'
            if (-not (Use-Jdk 17)) { return }
            Write-Step 'Data layer'
            foreach ($n in $DATA_SERVICES.Keys) { Start-SpringService $n $DATA_SERVICES[$n] }
            Wait-For-Port 8070 'gateway' 120 | Out-Null
            Write-Step 'Business layer'
            foreach ($n in $BIZ_SERVICES.Keys)  { Start-SpringService $n $BIZ_SERVICES[$n] }
            Start-Sleep 3
            Write-Step 'Angular UI'
            Start-NgServe $APP_REPO 4201 'serioplus-app'
            Write-Ok 'Stack started --> http://localhost:4201/serioplus/#/?acceptBanner=true'
        }
        'data' {
            Write-Step 'Starting data layer'
            if (-not (Use-Jdk 17)) { return }
            foreach ($n in $DATA_SERVICES.Keys) { Start-SpringService $n $DATA_SERVICES[$n] }
            Wait-For-Port 8070 'gateway' 120 | Out-Null
        }
        'business' {
            Write-Step 'Starting business layer'
            if (-not (Use-Jdk 17)) { return }
            if (-not (Port-Up 8070)) { Write-Warn 'Gateway :8070 not up -- start data tier first: serio start data' }
            foreach ($n in $BIZ_SERVICES.Keys) { Start-SpringService $n $BIZ_SERVICES[$n] }
        }
        'app' {
            Write-Step 'Starting SERIO+ Angular UI'
            Start-NgServe $APP_REPO 4201 'serioplus-app'
            Write-Ok '--> http://localhost:4201/serioplus/#/?acceptBanner=true'
        }
        'monolith' {
            Write-Step 'Starting SERIO monolith'
            if (-not (Use-Jdk 21)) { return }
            Start-Monolith
        }
        default {
            $def = $ALL_SERVICES[$t]
            if ($def) {
                if (-not (Use-Jdk 17)) { return }
                Write-Step "Starting $t"
                Start-SpringService $t $def
            } else {
                Write-Fail "Unknown target: '$t'"
                Write-Host '  Valid targets: all | data | business | app | monolith | <service-name>'
            }
        }
    }
}

function Invoke-Stop {
    param($t)
    switch ($t) {
        'all' {
            Write-Step 'Stopping SERIO+ stack'
            foreach ($n in $ALL_SERVICES.Keys) { Stop-Named $n }
            Stop-Named 'serioplus-app'
            Remove-Item $STATE_FILE -EA 0
        }
        'data'     { Write-Step 'Stopping data layer';     foreach ($n in $DATA_SERVICES.Keys) { Stop-Named $n } }
        'business' { Write-Step 'Stopping business layer'; foreach ($n in $BIZ_SERVICES.Keys)  { Stop-Named $n } }
        'app'      { Write-Step 'Stopping Angular UI';     Stop-Named 'serioplus-app' }
        'monolith' { Write-Step 'Stopping SERIO monolith'; Stop-Monolith }
        default    { Write-Step "Stopping $t"; Stop-Named $t }
    }
}

function Invoke-Restart {
    param($t)
    Write-Step "Restarting $t"
    Invoke-Stop $t
    Start-Sleep 2
    Invoke-Start $t
}

function Invoke-Build {
    param($t)
    switch ($t) {
        'common-lib' { Build-CommonLib }
        'data'       { Build-CommonLib; Build-Maven $DATA_REPO 'SERIOPlusDataServices' }
        'business'   { Build-Maven $SVC_REPO 'SERIOPlusServices' }
        'app'        { Build-App }
        'all'        { Build-CommonLib; Build-Maven $DATA_REPO 'SERIOPlusDataServices'; Build-Maven $SVC_REPO 'SERIOPlusServices'; Build-App }
        default      { Write-Fail "Unknown build target: '$t'  Valid: all | common-lib | data | business | app" }
    }
}

function Invoke-Status {
    Write-Host ''
    Write-Host '== SERIO Stack Status ==================================' -ForegroundColor Cyan

    $ports = @(
        @{Port=4200; Label='SERIO Angular (monolith)'}
        @{Port=4201; Label='SERIO+ Angular UI'}
        @{Port=7001; Label='WebLogic'}
        @{Port=8070; Label='local-gateway-service'}
        @{Port=8080; Label='general-admin-service'}
        @{Port=8081; Label='user-option-service'}
        @{Port=8082; Label='aiml-services'}
        @{Port=8083; Label='workflow-service'}
        @{Port=8084; Label='notice-service'}
        @{Port=8085; Label='screening-service'}
        @{Port=8086; Label='filer-eval-service'}
        @{Port=8090; Label='entry-data-service'}
        @{Port=8091; Label='lookup-data-service'}
        @{Port=8092; Label='user-org-data-service'}
        @{Port=8093; Label='work-data-service'}
        @{Port=8094; Label='application-service'}
        @{Port=8095; Label='document-service'}
        @{Port=8096; Label='screening-data-service'}
        @{Port=8097; Label='filer-eval-data-service'}
    )

    foreach ($s in $ports) {
        $up    = Port-Up $s.Port
        $dot   = if ($up) { '[UP]' } else { '[  ]' }
        $color = if ($up) { 'Green' } else { 'DarkGray' }
        Write-Host ('  {0}  :{1,-5}  {2}' -f $dot, $s.Port, $s.Label) -ForegroundColor $color
    }

    Write-Host ''
    Write-Host '== Tracked PIDs ========================================' -ForegroundColor Cyan
    $state = @(Load-State)
    if (-not $state) {
        Write-Info '(nothing tracked)'
    } else {
        foreach ($e in $state) {
            $alive = $null -ne (Get-Process -Id $e.Pid -EA 0)
            $dot   = if ($alive) { '[UP]' } else { '[  ]' }
            $color = if ($alive) { 'Green' } else { 'DarkGray' }
            Write-Host ('  {0}  {1,-48}  PID {2}' -f $dot, $e.Name, $e.Pid) -ForegroundColor $color
        }
    }
    Write-Host '========================================================' -ForegroundColor Cyan
    Write-Host ''
}

function Show-Help {
    Write-Host @"

  serio start   all | data | business | app | monolith | <service-name>
  serio stop    all | data | business | app | monolith | <service-name>
  serio restart all | data | business | app | monolith | <service-name>
  serio build   all | common-lib | data | business | app
  serio status

Examples:
  serio start all
  serio start monolith
  serio start serioplus-document-service
  serio restart business
  serio stop all
  serio status
  serio build all

"@
}

switch ($Command.ToLower()) {
    'start'   { if ($Target) { Invoke-Start   $Target } else { Show-Help } }
    'stop'    { if ($Target) { Invoke-Stop    $Target } else { Show-Help } }
    'restart' { if ($Target) { Invoke-Restart $Target } else { Show-Help } }
    'build'   { if ($Target) { Invoke-Build   $Target } else { Show-Help } }
    'status'  { Invoke-Status }
    default   { Show-Help }
}
