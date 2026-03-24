@echo off
REM GitHub Token Authentication Script
REM Run this script and paste your token when prompted

echo ========================================
echo GitHub Token Authentication
echo ========================================
echo.
echo Please create a token at: https://github.com/settings/tokens
echo Required permissions: repo (Full control of private repositories)
echo.

set /p TOKEN="Paste your GitHub Personal Access Token here: "

echo.
echo Authenticating...

REM Create gh config directory
mkdir "%USERPROFILE%\.config\gh" 2>nul

REM Authenticate with token
echo %TOKEN% | gh auth login --with-token

if errorlevel 1 (
    echo.
    echo Authentication failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Authentication successful!
echo ========================================
echo.
gh auth status
echo.
pause
