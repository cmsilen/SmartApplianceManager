
@echo off
REM ============================================================
REM  SmartApplianceManager UML Generator
REM  Generates class and package diagrams from Pyreverse
REM ============================================================

echo [INFO] Activating Conda environment: smart_env...
CALL conda activate smart_env

echo [INFO] Removing old UML diagrams...
del classes_EvalSystemCore.* >nul 2>&1
del packages_EvalSystemCore.* >nul 2>&1

echo [INFO] Generating UML diagrams in SVG format...
pyreverse -o svg -p EvalSystemCore evaluation_system/config evaluation_system/controller evaluation_system/errorlog evaluation_system/messaging evaluation_system/model evaluation_system/reporting evaluation_system/repository

IF EXIST classes_EvalSystemCore.svg (
    echo [SUCCESS] Class diagram generated: classes_EvalSystemCore.svg
) ELSE (
    echo [ERROR] Failed to generate class diagram.
)

IF EXIST packages_EvalSystemCore.svg (
    echo [SUCCESS] Package diagram generated: packages_EvalSystemCore.svg
) ELSE (
    echo [ERROR] Failed to generate package diagram.
)

echo [INFO] Opening output folder...
explorer .

echo [DONE] UML generation completed.
pause
