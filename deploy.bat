@echo off
REM Odoo MCP Server - Deployment Script for Windows

echo.
echo ===============================================
echo  Odoo MCP Server - Cloudflare Deployment
echo ===============================================
echo.

REM Check if wrangler is installed
where wrangler >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Wrangler CLI not found!
    echo.
    echo Please install Wrangler first:
    echo   npm install -g wrangler
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking authentication...
wrangler whoami >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Not logged in to Cloudflare. Opening browser...
    wrangler login
)

echo [2/4] Building project...
call npm run build >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed!
    echo.
    echo Run this command manually to see errors:
    echo   npm run build
    echo.
    pause
    exit /b 1
)

echo [3/4] Checking secrets configuration...
echo.
echo Make sure you've set these secrets:
echo   - ODOO_URL (or ODOO_INSTANCES)
echo   - ODOO_DB
echo   - ODOO_USERNAME
echo   - ODOO_PASSWORD
echo.
echo To set secrets, run:
echo   wrangler secret put ODOO_URL
echo   wrangler secret put ODOO_DB
echo   wrangler secret put ODOO_USERNAME
echo   wrangler secret put ODOO_PASSWORD
echo.

set /p CONTINUE="Have you configured secrets? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo.
    echo Deployment cancelled. Please configure secrets first.
    pause
    exit /b 0
)

echo.
echo [4/4] Deploying to Cloudflare Workers...
call wrangler deploy

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo  Deployment Successful!
    echo ===============================================
    echo.
    echo Your Odoo MCP Server is now live!
    echo.
    echo To view logs:
    echo   wrangler tail
    echo.
    echo To test:
    echo   Configure Claude Desktop with your worker URL
    echo.
) else (
    echo.
    echo [ERROR] Deployment failed!
    echo.
    echo Check the error messages above for details.
    echo.
)

pause
