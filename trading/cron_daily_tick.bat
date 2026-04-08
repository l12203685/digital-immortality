@echo off
REM Daily testnet tick — runs all 4 strategies, logs to results/testnet_log.jsonl
REM Add to Windows Task Scheduler: daily at 09:00 UTC (or any fixed daily time)
REM
REM Task Scheduler setup (run once in Admin PowerShell):
REM   $action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c C:\Users\admin\workspace\digital-immortality\trading\cron_daily_tick.bat"
REM   $trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
REM   Register-ScheduledTask -TaskName "DigitalImmortalityTestnetTick" -Action $action -Trigger $trigger -RunLevel Highest

cd /d C:\Users\admin\workspace\digital-immortality

REM Try python3 first, fallback to python
where python3 >nul 2>&1
if %errorlevel%==0 (
    python3 -m trading.testnet_runner --tick
) else (
    python -m trading.testnet_runner --tick
)
