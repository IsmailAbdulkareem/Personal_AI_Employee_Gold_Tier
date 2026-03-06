# AI Employee - LinkedIn Post Scheduler
# Runs Tue/Wed/Thu at 9:00 AM
# Generates and posts LinkedIn content

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsPath = Join-Path $scriptPath "..\AI_Employee_Vault\Logs"

# Create log entry
$logFile = Join-Path $logsPath "scheduler.log"
$logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - LinkedIn Post triggered"
Add-Content -Path $logFile -Value $logEntry

# Check if today is Tuesday, Wednesday, or Thursday
$dayOfWeek = (Get-Date).DayOfWeek
if ($dayOfWeek -eq 'Tuesday' -or $dayOfWeek -eq 'Wednesday' -or $dayOfWeek -eq 'Thursday') {
    # Generate a business insight post
    $topics = @(
        "business automation",
        "AI productivity",
        "digital transformation",
        "workflow optimization"
    )
    $randomTopic = $topics | Get-Random
    
    # Run LinkedIn poster in draft mode
    $postOutput = python (Join-Path $scriptPath "linkedin_poster.py") draft --type insight --topic $randomTopic
    
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - LinkedIn draft created for topic: $randomTopic"
    Add-Content -Path $logFile -Value $logEntry
    
    Write-Host "LinkedIn post draft created"
    Write-Host $postOutput
    Write-Host "`nMove the draft from Pending_Approval to Approved to publish"
} else {
    Write-Host "Not a scheduled posting day (Tue/Wed/Thu)"
}
