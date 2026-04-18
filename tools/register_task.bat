@echo off
REM Register the stale memory detector scheduled task
schtasks.exe /Create /TN Edward_StaleMemory_Check /XML C:\Users\admin\workspace\digital-immortality\tools\stale_detector_scheduler.xml /F
echo.
echo Verifying task registration...
schtasks.exe /Query /TN Edward_StaleMemory_Check /V /FO List
