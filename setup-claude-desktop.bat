@echo off
REM Odoo MCP Server - Claude Desktop Configuration Helper

echo.
echo ===============================================
echo  Odoo MCP Server - Claude Desktop Setup
echo ===============================================
echo.

set CONFIG_PATH=%APPDATA%\Claude\claude_desktop_config.json
set PROJECT_PATH=%~dp0

echo Configuration will be saved to:
echo %CONFIG_PATH%
echo.
echo Project directory:
echo %PROJECT_PATH%
echo.

REM Check if config file exists
if not exist "%CONFIG_PATH%" (
    echo [INFO] Config file doesn't exist. Creating new file...
    mkdir "%APPDATA%\Claude" 2>nul
)

echo.
echo ===============================================
echo  Configuration Options
echo ===============================================
echo.
echo Select configuration type:
echo.
echo 1. Single Odoo instance (recommended for beginners)
echo 2. Multiple Odoo instances (for advanced users)
echo 3. Show example configuration (don't modify config)
echo.

set /p CHOICE="Enter choice (1-3): "

if "%CHOICE%"=="3" goto :show_example
if "%CHOICE%"=="2" goto :multi_instance
if "%CHOICE%"=="1" goto :single_instance

echo Invalid choice!
pause
exit /b 1

:single_instance
echo.
echo ===============================================
echo  Single Instance Configuration
echo ===============================================
echo.
echo Enter your Odoo connection details:
echo.

set /p ODOO_URL="Odoo URL (e.g., http://localhost:8069): "
set /p ODOO_DB="Database name (e.g., odoo): "
set /p ODOO_USER="Username (e.g., admin): "
set /p ODOO_PASS="Password: "

echo.
echo Generating configuration...
echo.

(
echo {
echo   "mcpServers": {
echo     "odoo": {
echo       "command": "node",
echo       "args": ["%PROJECT_PATH%dist\\index.js"],
echo       "env": {
echo         "ODOO_URL": "%ODOO_URL%",
echo         "ODOO_DB": "%ODOO_DB%",
echo         "ODOO_USERNAME": "%ODOO_USER%",
echo         "ODOO_PASSWORD": "%ODOO_PASS%"
echo       }
echo     }
echo   }
echo }
) > "%CONFIG_PATH%"

echo Configuration saved to:
echo %CONFIG_PATH%
echo.
echo Please restart Claude Desktop to apply changes.
echo.
pause
exit /b 0

:multi_instance
echo.
echo ===============================================
echo  Multiple Instances Configuration
echo ===============================================
echo.
echo For multiple instances, you need to create a JSON configuration.
echo.
echo Example format:
echo {"local":{"url":"http://localhost:8069","db":"odoo","username":"admin","password":"admin"}}
echo.

set /p INSTANCES="Paste your ODOO_INSTANCES JSON (or press Enter to cancel): "

if "%INSTANCES%"=="" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Generating configuration...
echo.

(
echo {
echo   "mcpServers": {
echo     "odoo-multi": {
echo       "command": "node",
echo       "args": ["%PROJECT_PATH%dist\\index.js"],
echo       "env": {
echo         "ODOO_INSTANCES": "%INSTANCES%"
echo       }
echo     }
echo   }
echo }
) > "%CONFIG_PATH%"

echo Configuration saved to:
echo %CONFIG_PATH%
echo.
echo Please restart Claude Desktop to apply changes.
echo.
pause
exit /b 0

:show_example
echo.
echo ===============================================
echo  Example Configuration
echo ===============================================
echo.
echo Single instance example:
echo.
type nul > temp.txt
(
echo {
echo   "mcpServers": {
echo     "odoo": {
echo       "command": "node",
echo       "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
echo       "env": {
echo         "ODOO_URL": "http://localhost:8069",
echo         "ODOO_DB": "odoo",
echo         "ODOO_USERNAME": "admin",
echo         "ODOO_PASSWORD": "admin"
echo       }
echo     }
echo   }
echo }
)
echo.
echo Multiple instances example:
echo.
(
echo {
echo   "mcpServers": {
echo     "odoo-multi": {
echo       "command": "node",
echo       "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
echo       "env": {
echo         "ODOO_INSTANCES": "{\"local\":{\"url\":\"http://localhost:8069\",\"db\":\"odoo\",\"username\":\"admin\",\"password\":\"admin\"},\"production\":{\"url\":\"https://odoo.example.com\",\"db\":\"prod_db\",\"username\":\"api_user\",\"password\":\"secure_pass\"}}"
echo       }
echo     }
echo   }
echo }
)
echo.
echo Copy this to: %CONFIG_PATH%
echo.
pause
exit /b 0
