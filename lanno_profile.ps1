
function Get-LannoStatus {
    Write-Host "--- LANNO PRODUCTION STATUS ---" -ForegroundColor Cyan
    if (Test-Path "production/status_report.md") {
        Get-Content "production/status_report.md"
    } else {
        Write-Host "No status report found." -ForegroundColor Yellow
    }
    Write-Host "-------------------------------" -ForegroundColor Cyan
}

Set-Alias -Name status -Value Get-LannoStatus
