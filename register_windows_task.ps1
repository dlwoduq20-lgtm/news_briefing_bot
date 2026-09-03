# Windows 작업 스케줄러 등록 스크립트 (매일 아침 8시 실행)
$TaskName = "MorningNewsBriefingBot"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatPath = Join-Path $ScriptDir "run_daily.bat"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [Windows 작업 스케줄러 최적화 등록: 매일 아침 8시 실행]" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "실행 대상: $BatPath"

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $ScriptDir
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

# 기존 작업 삭제 후 재등록
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "매일 아침 8시 삼성전자/SK하이닉스/비트코인 심층 뉴스 브리핑 카카오톡 자동 전송" -Force

Write-Host "`n✅ 작업 스케줄러 등록 완료!" -ForegroundColor Green
Write-Host "작업 이름: $TaskName (매일 오전 08:00 실행)" -ForegroundColor Yellow
Write-Host "옵션: 절전 모드 자동 깨우기(WakeToRun) 및 부팅 시 놓친 작업 자동 실행(StartWhenAvailable) 적용됨`n"
