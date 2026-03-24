@echo off
REM GitHub Token Authentication Script
set /p TOKEN="请输入你的GitHub Personal Access Token: "
echo %TOKEN% | gh auth login --with-token
if errorlevel 1 (
    echo 认证失败，请检查Token是否正确
    pause
    exit /b 1
)
echo 认证成功！
gh auth status
pause
