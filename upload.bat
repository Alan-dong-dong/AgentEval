@echo off
REM AgentEval GitHub Upload Script
REM Usage: upload.bat YOUR_GITHUB_USERNAME

if "%1"=="" (
    echo Usage: upload.bat YOUR_GITHUB_USERNAME
    echo Example: upload.bat myusername
    exit /b 1
)

set USERNAME=%1

echo ========================================
echo AgentEval GitHub Upload Script
echo ========================================
echo.
echo GitHub Username: %USERNAME%
echo Repository: https://github.com/%USERNAME%/AgentEval
echo.

echo Step 1: Adding remote origin...
git remote add origin https://github.com/%USERNAME%/AgentEval.git
if errorlevel 1 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/%USERNAME%/AgentEval.git
)

echo Step 2: Renaming branch to main...
git branch -M main

echo Step 3: Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo Push failed! Please check:
    echo 1. Repository exists on GitHub
    echo 2. You have push access
    echo 3. Git credentials are configured
    echo.
    echo Create repository at: https://github.com/new
    exit /b 1
)

echo.
echo ========================================
echo Upload successful!
echo Repository: https://github.com/%USERNAME%/AgentEval
echo ========================================
