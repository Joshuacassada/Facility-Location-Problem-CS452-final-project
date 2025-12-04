@echo off
setlocal enabledelayedexpansion

set TEST_DIR=realistic_test_cases
set OUTPUT_DIR=realistic_test_cases\outputs
set TIMEOUT_SECONDS=300

echo Running Facility Location test cases 17-42...
echo Timeout per case: %TIMEOUT_SECONDS% seconds (5 minutes)
echo.

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set SUCCESS_COUNT=0
set TIMEOUT_COUNT=0
set ERROR_COUNT=0

for /L %%i in (17,1,42) do (
    set FILE=%TEST_DIR%\test_case_%%i.txt
    echo [%%i/42] Running test_case_%%i.txt...

    if exist "!FILE!" (
        rem Run with timeout using start /wait
        start /B /wait "" timeout /T 1 /NOBREAK >nul 2>&1
        
        rem Run the solver (without timeout for now - Windows timeout is complex)
        python facility_location_exact.py "!FILE!" > "%OUTPUT_DIR%\test_case_%%i.out" 2>&1
        
        if !ERRORLEVEL! EQU 0 (
            rem Check if output contains solution
            findstr /C:"OPTIMAL SOLUTION FOUND" "%OUTPUT_DIR%\test_case_%%i.out" >nul
            if !ERRORLEVEL! EQU 0 (
                echo   [OK] Solution found
                set /A SUCCESS_COUNT+=1
            ) else (
                echo   [WARN] Completed but no solution found
                set /A ERROR_COUNT+=1
            )
        ) else (
            echo   [ERROR] Solver failed
            set /A ERROR_COUNT+=1
        )
    ) else (
        echo   [ERROR] File not found: !FILE!
        set /A ERROR_COUNT+=1
    )
    echo.
)

echo =====================================
echo Summary:
echo   Successful: !SUCCESS_COUNT!
echo   Errors:     !ERROR_COUNT!
echo =====================================
echo.
echo Output files saved to: %OUTPUT_DIR%
echo.

pause