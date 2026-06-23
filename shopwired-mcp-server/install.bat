@echo off
REM ShopWired MCP Server - one-click installer (Windows)
REM
REM What this does:
REM   1. Ensures uv is installed (installs it if missing)
REM   2. Installs dependencies from the locked versions (uv sync)
REM   3. Collects your ShopWired API credentials
REM   4. Registers the server with Claude Code
REM
REM Run it from inside the project folder:  install.bat
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
set "SERVER_NAME=shopwired"

echo ==^> ShopWired MCP installer
echo     Installing from: %PROJECT_DIR%
echo.

REM --- Step 1: ensure uv is available ---
where uv >nul 2>nul
if errorlevel 1 (
  echo ==^> 'uv' not found - installing it...
  powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
for /f "delims=" %%v in ('uv --version') do echo ==^> uv: %%v
echo.

REM --- Step 2: install dependencies ---
echo ==^> Installing dependencies (this may take a minute on first run)...
pushd "%PROJECT_DIR%"
uv sync
popd
echo ==^> Dependencies installed.
echo.

REM --- Step 3: collect credentials ---
:get_key
set "API_KEY="
set /p "API_KEY=ShopWired API Key: "
if "!API_KEY!"=="" ( echo   (required - please enter your API key) & goto get_key )

:get_secret
set "API_SECRET="
set /p "API_SECRET=ShopWired API Secret: "
if "!API_SECRET!"=="" ( echo   (required - please enter your API secret) & goto get_secret )

REM --- Step 4: register with Claude Code ---
where claude >nul 2>nul
if errorlevel 1 (
  echo ==^> Claude Code CLI not found. Add this to your Claude Desktop config manually:
  echo     %%APPDATA%%\Claude\claude_desktop_config.json
  echo.
  echo   "mcpServers": {
  echo     "%SERVER_NAME%": {
  echo       "command": "uv",
  echo       "args": ["run", "--directory", "%PROJECT_DIR%", "shopwired-mcp"],
  echo       "env": {
  echo         "SHOPWIRED_API_KEY": "!API_KEY!",
  echo         "SHOPWIRED_API_SECRET": "!API_SECRET!"
  echo       }
  echo     }
  echo   }
) else (
  echo ==^> Registering '%SERVER_NAME%' with Claude Code...
  claude mcp add "%SERVER_NAME%" --env "SHOPWIRED_API_KEY=!API_KEY!" --env "SHOPWIRED_API_SECRET=!API_SECRET!" -- uv run --directory "%PROJECT_DIR%" shopwired-mcp
  echo ==^> Done. Restart Claude Code and the ShopWired tools will be available.
)

endlocal
