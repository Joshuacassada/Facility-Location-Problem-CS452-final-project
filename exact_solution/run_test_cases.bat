@echo off
setlocal enabledelayedexpansion

set TEST_DIR=realistic_test_cases
set OUTPUT_DIR=realistic_test_cases\outputs

echo Running first 25 Facility Location test cases...

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

for /L %%i in (17,1,42) do (
    set FILE=%TEST_DIR%\test_case_%%i.txt
    echo === Running test_case_%%i.txt ===

    if exist "!FILE!" (
        python facility_location_exact.py "!FILE!" > "%OUTPUT_DIR%\test_case_%%i.out"
        echo Output saved to %OUTPUT_DIR%\test_case_%%i.out
    ) else (
        echo File not found: !FILE!
    )
)

echo Done running first 25 tests.
pause
