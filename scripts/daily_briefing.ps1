# AI Employee - Daily Briefing
# Runs every day at 8:00 AM
# Generates daily briefing and updates dashboard

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$vaultPath = Join-Path $scriptPath "AI_Employee_Vault"
$dashboardPath = Join-Path $vaultPath "Dashboard.md"
$logsPath = Join-Path $vaultPath "Logs"

# Create log entry
$logFile = Join-Path $logsPath "scheduler.log"
$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Daily Briefing triggered"
Add-Content -Path $logFile -Value $logEntry

# Update dashboard timestamp
if (Test-Path $dashboardPath) {
    $content = Get-Content -Path $dashboardPath -Raw
    $newDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $content = $content -replace 'last_updated: .*', "last_updated: $newDate`n"
    Set-Content -Path $dashboardPath -Value $content
    
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Dashboard updated"
    Add-Content -Path $logFile -Value $logEntry
}

# Trigger Claude Code for briefing generation
# Note: This requires Claude Code to be installed and configured
# claude "Generate a daily briefing based on the tasks in Done folder and update the Dashboard"

Write-Host "Daily Briefing completed at $(Get-Date)"
