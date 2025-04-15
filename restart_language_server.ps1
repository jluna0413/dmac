# This script will help restart the Python Language Server in VS Code
# Run this script from PowerShell

Write-Host "This script will help restart the Python Language Server in VS Code" -ForegroundColor Green
Write-Host "Please follow these steps:" -ForegroundColor Yellow

Write-Host "1. In VS Code, press Ctrl+Shift+P to open the Command Palette" -ForegroundColor Cyan
Write-Host "2. Type 'Python: Restart Language Server' and select that command" -ForegroundColor Cyan
Write-Host "3. Wait for the language server to restart" -ForegroundColor Cyan
Write-Host "4. If the error persists, try restarting VS Code completely" -ForegroundColor Cyan

Write-Host "`nAdditional steps if the error persists:" -ForegroundColor Yellow
Write-Host "1. In VS Code, press Ctrl+Shift+P to open the Command Palette" -ForegroundColor Cyan
Write-Host "2. Type 'Developer: Reload Window' and select that command" -ForegroundColor Cyan
Write-Host "3. Wait for VS Code to reload" -ForegroundColor Cyan

Write-Host "`nIf the error still persists, try clearing the VS Code workspace storage:" -ForegroundColor Yellow
Write-Host "1. Close VS Code" -ForegroundColor Cyan
Write-Host "2. Delete the .vscode/.pylance directory if it exists" -ForegroundColor Cyan
Write-Host "3. Restart VS Code" -ForegroundColor Cyan

Write-Host "`nPress any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
