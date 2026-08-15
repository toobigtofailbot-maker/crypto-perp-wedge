[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HermesProjectHome,

    [Parameter(Mandatory = $true)]
    [string]$HermesModel,

    [string]$ResearchMemoryReadOnlyDsn = "",

    [switch]$InstallSchedules
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $scriptRoot "..\.."))
$hermesHome = [System.IO.Path]::GetFullPath($HermesProjectHome)
$outbox = [System.IO.Path]::GetFullPath(
    (Join-Path $repoRoot "scratch\hermes_proposal_outbox")
)

if ($hermesHome.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar)) {
    throw "HermesProjectHome must be separate from the repository"
}
if (Test-Path -LiteralPath $hermesHome) {
    $homeItem = Get-Item -LiteralPath $hermesHome -Force
    if ($homeItem.LinkType) {
        throw "HermesProjectHome must not be a symlink or junction"
    }
} else {
    New-Item -ItemType Directory -Path $hermesHome | Out-Null
}
if (Test-Path -LiteralPath $outbox) {
    $outboxItem = Get-Item -LiteralPath $outbox -Force
    if ($outboxItem.LinkType) {
        throw "Hermes proposal outbox must not be a symlink or junction"
    }
} else {
    New-Item -ItemType Directory -Path $outbox | Out-Null
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required for the isolated Hermes deployment"
}

$repoSha = (& git -C $repoRoot rev-parse HEAD).Trim()
$repoBranch = (& git -C $repoRoot branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $repoSha -notmatch '^[0-9a-f]{40}$' -or -not $repoBranch) {
    throw "Unable to resolve exact repository identity"
}

$env:HERMES_PROJECT_HOME = $hermesHome
$env:HERMES_PROPOSAL_OUTBOX_HOST = $outbox
$env:HERMES_MODEL = $HermesModel
$env:PROJECT_REPO_SHA = $repoSha
$env:PROJECT_REPO_BRANCH = $repoBranch
$env:RESEARCH_MEMORY_READONLY_DSN = $ResearchMemoryReadOnlyDsn

$compose = Join-Path $scriptRoot "compose.yaml"
& docker compose -f $compose config --quiet
if ($LASTEXITCODE -ne 0) { throw "Hermes compose validation failed" }
& docker compose -f $compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "Hermes deployment startup failed" }

if ($InstallSchedules) {
    $plan = Get-Content -LiteralPath (Join-Path $scriptRoot "schedule_plan.json") -Raw |
        ConvertFrom-Json
    $existing = (& docker compose -f $compose exec -T hermes hermes cron list) -join "`n"
    if ($LASTEXITCODE -ne 0) { throw "Unable to inspect existing Hermes schedules" }
    foreach ($job in $plan.jobs) {
        if ($existing -notmatch [regex]::Escape($job.name)) {
            & docker compose -f $compose exec -T hermes hermes cron create `
                $job.schedule $job.prompt --skill $job.skill --deliver $job.deliver --name $job.name
            if ($LASTEXITCODE -ne 0) { throw "Failed to create schedule: $($job.name)" }
        }
    }
}

Write-Output "Hermes deployment started for repo SHA $repoSha"
Write-Output "Project write surface: $outbox"
