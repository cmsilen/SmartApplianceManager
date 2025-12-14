@echo off
REM ============================================================
REM  SmartApplianceManager UML Generator - Preparation System
REM  Generates class and package diagrams (SVG) using Pyreverse
REM ============================================================

echo [INFO] Activating Conda environment: smart_env...
CALL conda activate smart_env

echo [INFO] Removing old UML diagrams...
del classes_PrepSystemCore.* >nul 2>&1
del packages_PrepSystemCore.* >nul 2>&1

echo [INFO] Generating UML diagrams in SVG format...
pyreverse -o svg -p PrepSystemCore "C:/Users/mesay/PycharmProjects/SmartApplianceManager/evaluation_system/src"

IF EXIST classes_PrepSystemCore.svg (
    echo [SUCCESS] Class diagram generated: classes_PrepSystemCore.svg
) ELSE (
    echo [ERROR] Failed to generate class diagram.
)

IF EXIST packages_PrepSystemCore.svg (
    echo [SUCCESS] Package diagram generated: packages_PrepSystemCore.svg
) ELSE (
    echo [ERROR] Failed to generate package diagram.
)

echo [INFO] Opening UML output folder...
explorer .

echo [DONE] UML generation completed successfully.
pause
