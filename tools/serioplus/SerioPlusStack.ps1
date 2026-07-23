#Requires -Version 5.1
<#
.SYNOPSIS
    Build and run the full SERIO+ stack (common-lib -> data layer -> business layer -> UI).

.DESCRIPTION
    One script to build every SERIO+ repo in dependency order and start the services bottom-up,
    or to stop/query a running stack.

    Build order (dependencies first):
      1. SERIOPlusCommonLibraries  - shared JAR (serioplus-common-library:13.0.0-SNAPSHOT)
      2. shared-ui-component-library - Angular npm lib (@ora/shared-service-common-ui)
      3. SERIOPlusDataServices     - data tier (8 Spring Boot services + gateway :8070)
      4. SERIOPlusServices         - business tier (7 Spring Boot services :8080-8086)
      5. SERIOPlusApp              - Angular UI (ng serve :4201)

    Start order (bottom-up):
      Tier 1: SERIOPlusDataServices jars (:8090-8097) + local-gateway-service (:8070)
      Tier 2: SERIOPlusServices jars (:8080-8086)
      Tier 3: SERIOPlusApp (ng serve :4201)

    ACTIONS:
      build    Build in order: common-lib -> shared-ui -> data -> services -> app
      start    Start: data jars -> wait for gateway :8070 -> business jars -> ng serve :4201
      stop     Stop all tracked processes
      status   Show tracked processes and whether their ports respond
      restart  stop then start

    PROFILES:
      local    Use --spring.profiles.active=local (reads classpath .properties, no AWS SSM).
               Use this when running without AWS credentials.
      server   Use --spring.profiles.active=server (reads from AWS SSM Parameter Store).
               Use this for the full environment (default in SerioPlusStack).

.PARAMETER Action
    build | start | stop | status | restart  (default: status)

.PARAMETER Only
    Limit to one component: common-lib | shared-ui | data | services | app

.PARAMETER Profile
    Spring profile: local | server  (default: local — safe for off-AWS dev)

.PARAMETER Root
    Folder containing the repos. Default: C:\projects

.PARAMETER SkipTests
    Pass -DskipTests to Maven (default: ON). Use -SkipTests:$false to run tests.

.PARAMETER DryRun
    Show what would happen; change nothing.

.EXAMPLE
    .\SerioPlusStack.ps1 -Action build
    .\SerioPlusStack.ps1 -Action start
    .\SerioPlusStack.ps1 -Action start -Profile server
    .\SerioPlusStack.ps1 -Action status
    .\SerioPlusStack.ps1 -Action stop
    .\SerioPlusStack.ps1 -Action build -Only data
    .\SerioPlusStack.ps1 -Action start -Only data

.NOTES
    PREREQUISITES
    - FDA laptop, full-tunnel VPN up (Nexus + Oracle reachable)
    - JDK 17 on PATH (SERIO+ does NOT build on JDK 21 — Lombok breaks)
    - Maven on PATH
    - Node / npm / ng on PATH
    - ~/.m2/settings.xml pointing at FDA Nexus
    - SERIOPlusApp/.npmrc copied from .npmrc.example (Nexus npm registry)
    - OASIS Oracle DB reachable for the data layer to function

    Logs + PID state are written to C:\projects\.serioplus-stack\ (outside any repo).

    See: C:\projects\aitools\skills\serioplus-data-services\SKILL.md
         C:\projects\aitools\skills\serioplus-business-services\SKILL.md
         C:\projects\aitools\skills\serioplus-app\SKILL.md
#>

[CmdletBinding()]
param(
    [ValidateSet('build','start','stop','status','restart')] [string] $Action  = 'status',
    [ValidateSet('common-lib','shared-ui','data','services','app')]    [string] $Only,
    [ValidateSet('local','server')]                                    [string] $Profile  = 'local',
    [string] $Root       = 'C:\projects',
    [switch] $SkipTests  = $true,
    [switch] $DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Step { param($m) Write-Host "`n==> $m" -ForegroundColor Cyan }
function Ok   { param($m) Write-Host "    $m" -ForegroundColor Green }
function Warn  { param($m) Write-Host "    WARN: $m" -ForegroundColor Yellow }
function Fail  { param($m) Write-Host "    ERROR: $m" -ForegroundColor Red }

# ── Repo map ─────────────────────────────────────────────────────────────────
$Repos = @{
    'common-lib' = 'SERIOPlusCommonLibraries'
    'shared-ui'  = 'shared-ui-component-library'
    'data'       = 'SERIOPlusDataServices'
    'services'   = 'SERIOPlusServices'
    'app'        = 'SERIOPlusApp'
}
$BuildOrder = @('common-lib','shared-ui','data','services','app')

# Data-tier ports (for health-check after start)
$DataPorts    = @(8090,8091,8092,8093,8094,8095,8096,8097)
$GatewayPort  = 8070
$BusinessPorts = @(8080,8081,8082,8083,8084,8085,8086)
$AppPort      = 4201

$StateDir  = Join-Path $Root '.serioplus-stack'
$StateFile = Join-Path $StateDir 'state.json'
$mvnFlag   = if ($SkipTests) { '-DskipTests' } else { '' }

function RepoPath { param($Key) Join-Path $Root $Repos[$Key] }

# ── Helpers ──────────────────────────────────────────────────────────────────
function Assert-Tool {
    param($Name, $Hint='')
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "'$Name' not found on PATH.$( if ($Hint) { " $Hint" })"
    }
}

function Set-Jdk17 {
    $candidates = @(
        'C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot',
        'C:\Program Files\Eclipse Adoptium\jdk-17.0.15.6-hotspot',
        'C:\Program Files\Java\jdk-17'
    )
    $jdk = $candidates | Where-Object { Test-Path "$_\bin\java.exe" } | Select-Object -First 1
    if (-not $jdk) {
        # Try discovering under Adoptium
        $jdk = Get-ChildItem 'C:\Program Files\Eclipse Adoptium' -Directory -EA 0 |
               Where-Object { $_.Name -match 'jdk-17' -and (Test-Path "$($_.FullName)\bin\java.exe") } |
               Select-Object -First 1 | ForEach-Object { $_.FullName }
    }
    if (-not $jdk) { throw "JDK 17 not found. SERIO+ requires JDK 17 (not 21+). Install Eclipse Adoptium JDK 17." }
    $env:JAVA_HOME = $jdk
    $env:PATH = "$jdk\bin;$env:PATH"
    Ok "JAVA_HOME = $jdk"
}

function Wait-Port {
    param([int]$Port, [int]$TimeoutSec=120, [string]$Label='')
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $label = if ($Label) { $Label } else { ":$Port" }
    Write-Host "    Waiting for $label..." -NoNewline -ForegroundColor DarkGray
    while ((Get-Date) -lt $deadline) {
        try {
            $c = New-Object Net.Sockets.TcpClient
            $c.Connect('127.0.0.1', $Port)
            $c.Close()
            Write-Host " UP" -ForegroundColor Green
            return $true
        } catch { Write-Host "." -NoNewline -ForegroundColor DarkGray; Start-Sleep 3 }
    }
    Write-Host " TIMEOUT" -ForegroundColor Red
    return $false
}

function Test-BootJar {
    param($JarPath)
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -EA 0
        $zip = [System.IO.Compression.ZipFile]::OpenRead($JarPath)
        try {
            $e = $zip.GetEntry('META-INF/MANIFEST.MF')
            if (-not $e) { return $false }
            $sr = New-Object System.IO.StreamReader($e.Open())
            $mf = $sr.ReadToEnd(); $sr.Close()
            return ($mf -match 'Spring-Boot-Version|JarLauncher|Start-Class')
        } finally { $zip.Dispose() }
    } catch { return $false }
}

function Get-BootJars {
    param($RepoKey)
    $repo = RepoPath $RepoKey
    Get-ChildItem -Path $repo -Recurse -Filter '*.jar' -File -EA 0 |
        Where-Object { $_.FullName -match '[\\/]target[\\/]' -and
                       $_.Name -notmatch '\.(original|sources|javadoc)\.jar$' } |
        Where-Object { Test-BootJar $_.FullName }
}

function Load-State { if (Test-Path $StateFile) { Get-Content $StateFile -Raw | ConvertFrom-Json } else { @() } }
function Save-State {
    param($State)
    New-Item -ItemType Directory -Force $StateDir | Out-Null
    ($State | ConvertTo-Json -Depth 5) | Set-Content $StateFile -Encoding utf8
}

function Kill-By-Cmdline {
    # Kill all java.exe processes whose command line matches a pattern (for cleanup before rebuild)
    param([string]$Pattern)
    Get-CimInstance Win32_Process -Filter "Name='java.exe'" -EA 0 |
        Where-Object { $_.CommandLine -like "*$Pattern*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA 0; Ok "Killed java PID $($_.ProcessId) ($Pattern)" }
}

# ── BUILD ─────────────────────────────────────────────────────────────────────
function Build-One {
    param($Key)
    $repo = RepoPath $Key
    if (-not (Test-Path $repo)) { Warn "$Key: repo not found at $repo — skipping."; return }
    Step "BUILD $Key  ($($Repos[$Key]))"

    switch ($Key) {
        'common-lib' {
            # Must install as 13.0.0-SNAPSHOT (what the services depend on)
            $pomDir = Join-Path $repo 'serioplus-common-library'
            if (-not (Test-Path $pomDir)) { $pomDir = $repo }  # fallback if flat
            if ($DryRun) { Ok "would: (in $pomDir) mvn '-Drevision=13.0.0-SNAPSHOT' $mvnFlag clean install"; return }
            Assert-Tool mvn
            Set-Jdk17
            Push-Location $pomDir
            try {
                & mvn '-Drevision=13.0.0-SNAPSHOT' $mvnFlag clean install
                if ($LASTEXITCODE -ne 0) { Fail "common-lib build failed (exit $LASTEXITCODE)"; Pop-Location; return }
            } finally { Pop-Location }
            Ok "common-lib installed as 13.0.0-SNAPSHOT"
        }
        'shared-ui' {
            # Angular library — find the package.json that has build-lib
            $pkg = Get-ChildItem $repo -Recurse -Filter 'package.json' -File -EA 0 |
                   Where-Object { (Get-Content $_.FullName -Raw -EA 0) -match '"build-lib"' } |
                   Select-Object -First 1
            if (-not $pkg) { Warn "shared-ui: no package.json with 'build-lib' found — skipping."; return }
            $dir = Split-Path $pkg.FullName -Parent
            if ($DryRun) { Ok "would: (in $dir) npm install; npm run build-lib"; return }
            Assert-Tool npm
            Push-Location $dir
            try {
                & npm install
                if ($LASTEXITCODE -ne 0) { Fail "npm install failed in $dir"; Pop-Location; return }
                & npm run build-lib
                if ($LASTEXITCODE -ne 0) { Fail "npm run build-lib failed in $dir"; Pop-Location; return }
            } finally { Pop-Location }
            Ok "shared-ui built"
        }
        'data' {
            if ($DryRun) { Ok "would: (in $repo) mvn $mvnFlag -nsu clean install; also build local-gateway-service"; return }
            Assert-Tool mvn
            Set-Jdk17
            Push-Location $repo
            try {
                & mvn $mvnFlag -nsu clean install
                if ($LASTEXITCODE -ne 0) { Fail "SERIOPlusDataServices build failed"; Pop-Location; return }
            } finally { Pop-Location }
            # Build the local-gateway-service if it's not in the main reactor
            $gwPom = Join-Path $repo 'local-gateway-service\pom.xml'
            if (Test-Path $gwPom) {
                $gwDir = Split-Path $gwPom
                Push-Location $gwDir
                try {
                    & mvn $mvnFlag -nsu clean install
                    if ($LASTEXITCODE -ne 0) { Warn "local-gateway-service build failed (non-fatal — gateway may already be built)" }
                } finally { Pop-Location }
            }
            Ok "SERIOPlusDataServices built"
        }
        'services' {
            if ($DryRun) { Ok "would: (in $repo) mvn $mvnFlag -nsu clean install"; return }
            Assert-Tool mvn
            Set-Jdk17
            Push-Location $repo
            try {
                & mvn $mvnFlag -nsu clean install
                if ($LASTEXITCODE -ne 0) { Fail "SERIOPlusServices build failed"; Pop-Location; return }
            } finally { Pop-Location }
            Ok "SERIOPlusServices built"
        }
        'app' {
            if ($DryRun) { Ok "would: (in $repo) [copy .npmrc] npm install"; return }
            Assert-Tool npm
            Push-Location $repo
            try {
                if (-not (Test-Path '.npmrc') -and (Test-Path '.npmrc.example')) {
                    Copy-Item '.npmrc.example' '.npmrc'
                    Ok "Copied .npmrc.example -> .npmrc"
                }
                & npm install
                if ($LASTEXITCODE -ne 0) { Fail "npm install failed in SERIOPlusApp"; Pop-Location; return }
            } finally { Pop-Location }
            Ok "SERIOPlusApp npm install done (run 'start -Only app' to serve)"
        }
    }
}

function Build-All {
    foreach ($k in $BuildOrder) {
        if (-not $Only -or $Only -eq $k) { Build-One $k }
    }
}

# ── START ─────────────────────────────────────────────────────────────────────
function Start-Jar {
    param($Jar, $Tier)
    $name = [IO.Path]::GetFileNameWithoutExtension($Jar.Name)
    $log  = Join-Path $StateDir "$name.log"
    $errlog = "$log.err"
    New-Item -ItemType Directory -Force $StateDir | Out-Null

    if ($DryRun) { Ok "would start [$Tier] $name  --  log: $name.log"; return $null }

    $p = Start-Process -FilePath 'java' `
        -ArgumentList @("-Dspring.profiles.active=$Profile", '-jar', "`"$($Jar.FullName)`"") `
        -RedirectStandardOutput $log -RedirectStandardError $errlog `
        -PassThru -WindowStyle Hidden

    Ok "started [$Tier] $name  (PID $($p.Id))  ->  $name.log"
    return [pscustomobject]@{
        Name  = $name
        Tier  = $Tier
        Pid   = $p.Id
        Jar   = $Jar.FullName
        Log   = $log
        Port  = $null
    }
}

function Start-All {
    Assert-Tool java
    $state = [System.Collections.Generic.List[object]]::new()

    # ── Tier 1: Data layer + gateway ─────────────────────────────────────────
    if (-not $Only -or $Only -eq 'data') {
        Step "Tier 1 — SERIOPlusDataServices (:8090-8097) + gateway (:8070)"
        Warn "Data layer needs OASIS Oracle DB reachable (full-tunnel VPN up, tunnel to gi-22040-22041.fda.gov:1523)"
        if ($Profile -eq 'local') { Warn "Profile=local: services read classpath .properties (no AWS SSM)" }

        $dataJars = @(Get-BootJars 'data')
        if (-not $dataJars) {
            Warn "No Spring Boot jars found under $(RepoPath 'data') — run '-Action build' first."
        } else {
            foreach ($j in $dataJars) {
                $r = Start-Jar $j 'data'
                if ($r) { $state.Add($r) }
            }
            if (-not $DryRun) {
                Ok "Waiting for local-gateway-service on :$GatewayPort (timeout 120s)..."
                if (Wait-Port $GatewayPort 120 "gateway :$GatewayPort") {
                    Ok "Gateway is up."
                } else {
                    Warn "Gateway did not answer on :$GatewayPort in time — check $(Join-Path $StateDir 'local-gateway-service.log')"
                }
            }
        }
    }

    # ── Tier 2: Business layer ────────────────────────────────────────────────
    if (-not $Only -or $Only -eq 'services') {
        Step "Tier 2 — SERIOPlusServices (:8080-8086)"
        $svcJars = @(Get-BootJars 'services')
        if (-not $svcJars) {
            Warn "No Spring Boot jars under $(RepoPath 'services') — run '-Action build' first."
        } else {
            foreach ($j in $svcJars) {
                $r = Start-Jar $j 'services'
                if ($r) { $state.Add($r) }
            }
            if (-not $DryRun) { Start-Sleep 5 }
        }
    }

    # ── Tier 3: Angular UI ────────────────────────────────────────────────────
    if (-not $Only -or $Only -eq 'app') {
        Step "Tier 3 — SERIOPlusApp (ng serve :$AppPort)"
        $appRepo = RepoPath 'app'
        $log = Join-Path $StateDir 'app-ngserve.log'
        if ($DryRun) {
            Ok "would: (in $appRepo) npm start   ->  http://localhost:$AppPort/serioplus/"
        } else {
            Assert-Tool npm
            $p = Start-Process -FilePath 'cmd.exe' `
                -ArgumentList '/c', "npm start > `"$log`" 2>&1" `
                -WorkingDirectory $appRepo -PassThru -WindowStyle Hidden
            Ok "started [app] ng serve (PID $($p.Id))  ->  http://localhost:$AppPort/serioplus/"
            Ok "log: $log"
            $state.Add([pscustomobject]@{ Name='app-ngserve'; Tier='app'; Pid=$p.Id; Jar=''; Log=$log; Port=$AppPort })
        }
    }

    if (-not $DryRun) {
        Save-State $state
        Ok "`nTracked $($state.Count) process(es).  Stop with: SerioPlusStack.ps1 -Action stop"
        Ok "State: $StateFile  |  Logs: $StateDir"
    }
}

# ── STOP ──────────────────────────────────────────────────────────────────────
function Stop-All {
    Step "STOP"
    $state = @(Load-State)
    if (-not $state) { Ok 'Nothing tracked. Use -Action start.'; return }
    foreach ($s in $state) {
        try {
            $p = Get-Process -Id $s.Pid -ErrorAction Stop
            if ($DryRun) { Ok "would stop $($s.Name) (PID $($s.Pid))"; continue }
            Stop-Process -Id $s.Pid -Force
            Ok "stopped $($s.Name) (PID $($s.Pid))"
        } catch {
            Warn "$($s.Name) (PID $($s.Pid)) not running."
        }
    }
    if (-not $DryRun) {
        Remove-Item $StateFile -ErrorAction SilentlyContinue
        Ok "State cleared."
    }
}

# ── STATUS ────────────────────────────────────────────────────────────────────
function Show-Status {
    Step "STATUS"
    $state = @(Load-State)
    if (-not $state) { Ok 'Nothing tracked. Use -Action start.'; return }

    $rows = foreach ($s in $state) {
        $alive = $null -ne (Get-Process -Id $s.Pid -EA 0)
        [pscustomobject]@{
            Name    = $s.Name
            Tier    = $s.Tier
            PID     = $s.Pid
            Running = if ($alive) { 'YES' } else { 'NO' }
            Log     = Split-Path $s.Log -Leaf
        }
    }
    $rows | Format-Table -AutoSize | Out-String -Width 180 | Write-Host
    Ok "Log dir: $StateDir"

    # Quick port check
    $ports = @($DataPorts + $GatewayPort + $BusinessPorts + $AppPort)
    $portRows = foreach ($port in $ports) {
        $up = $false
        try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',$port); $c.Close(); $up = $true } catch {}
        [pscustomobject]@{ Port = $port; Status = if ($up) { 'UP' } else { '--' } }
    }
    $portRows | Format-Table -AutoSize | Out-String -Width 80 | Write-Host
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
Step "SERIO+ Stack — action: $Action$(if ($DryRun) { ' (DRY RUN)' }$(if ($Only) { "  only: $Only" }))"
Ok "Root: $Root  |  Profile: $Profile  |  Logs: $StateDir"

switch ($Action) {
    'build'   { Build-All }
    'start'   { Start-All }
    'stop'    { Stop-All }
    'restart' { Stop-All; Start-Sleep 2; Start-All }
    'status'  { Show-Status }
}
