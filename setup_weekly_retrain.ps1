# PowerShell script to set up Windows Task Scheduler for weekly XGBoost retraining
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "XGBoost Weekly Retraining Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$projectPath = Get-Location
Write-Host "Project Path: $projectPath" -ForegroundColor Yellow
Write-Host ""

# Check if batch file exists
$batchFile = Join-Path $projectPath "run_weekly_retrain.bat"
if (-not (Test-Path $batchFile)) {
    Write-Host "ERROR: run_weekly_retrain.bat not found!" -ForegroundColor Red
    Write-Host "Expected location: $batchFile" -ForegroundColor Red
    exit 1
}

Write-Host "Found batch file: $batchFile" -ForegroundColor Green
Write-Host ""

# Check if Python script exists
$pythonScript = Join-Path $projectPath "weekly_retrain.py"
if (-not (Test-Path $pythonScript)) {
    Write-Host "ERROR: weekly_retrain.py not found!" -ForegroundColor Red
    Write-Host "Expected location: $pythonScript" -ForegroundColor Red
    exit 1
}

Write-Host "Found Python script: $pythonScript" -ForegroundColor Green
Write-Host ""

# Create directories if they don't exist
$logsDir = Join-Path $projectPath "logs\retraining"
$modelsDir = Join-Path $projectPath "models\weekly"

if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "Created directory: $logsDir" -ForegroundColor Green
}

if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
    Write-Host "Created directory: $modelsDir" -ForegroundColor Green
}

Write-Host ""

# Check if task already exists
$taskName = "XGBoost Weekly Retrain"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$taskName' already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to replace it? (Y/N)"
    
    if ($response -eq "Y" -or $response -eq "y") {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Removed existing task" -ForegroundColor Green
    } else {
        Write-Host "Setup cancelled" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Creating scheduled task..." -ForegroundColor Cyan

# Create action
$action = New-ScheduledTaskAction -Execute $batchFile -WorkingDirectory $projectPath

# Create trigger (every Sunday at 8 PM)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 8PM

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 10) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Automated weekly retraining of XGBoost model on latest prediction_log.csv" `
        -ErrorAction Stop | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Task created successfully" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: Every Sunday at 8:00 PM" -ForegroundColor White
    Write-Host "  Script: $batchFile" -ForegroundColor White
    Write-Host "  Working Directory: $projectPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the task by running it manually" -ForegroundColor White
    Write-Host "  2. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
    Write-Host "  3. Find '$taskName' in the task list" -ForegroundColor White
    Write-Host "  4. Right-click -> Run" -ForegroundColor White
    Write-Host "  5. Check logs\retraining\ for the report" -ForegroundColor White
    Write-Host ""
    Write-Host "To test now, run:" -ForegroundColor Yellow
    Write-Host "  python weekly_retrain.py" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running this script as Administrator:" -ForegroundColor Yellow
    Write-Host "  Right-click PowerShell -> Run as Administrator" -ForegroundColor White
    Write-Host "  cd $projectPath" -ForegroundColor White
    Write-Host "  .\setup_weekly_retrain.ps1" -ForegroundColor White
    exit 1
}

# Ask if user wants to test now
Write-Host ""
$testNow = Read-Host "Do you want to test the task now? (Y/N)"

if ($testNow -eq "Y" -or $testNow -eq "y") {
    Write-Host ""
    Write-Host "Running task..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName
    
    Write-Host ""
    Write-Host "Task started! Check the output in a few seconds..." -ForegroundColor Green
    Write-Host ""
    Write-Host "To view the report:" -ForegroundColor Yellow
    Write-Host "  type logs\retraining\$(Get-Date -Format 'yyyy-MM-dd')_report.txt" -ForegroundColor White
    Write-Host ""
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
