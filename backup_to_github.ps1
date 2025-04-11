# This script will help backup the project to GitHub
# Run this script from PowerShell

Write-Host "DMac GitHub Backup Script" -ForegroundColor Green
Write-Host "This script will help you backup your project to GitHub" -ForegroundColor Yellow

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git is not installed. Please install Git before proceeding." -ForegroundColor Red
    exit
}

# Check if the current directory is a git repository
if (-not (Test-Path ".git")) {
    Write-Host "This directory is not a git repository. Please run this script from the root of your DMac project." -ForegroundColor Red
    exit
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "You have uncommitted changes:" -ForegroundColor Yellow
    git status
    
    $commitMessage = Read-Host "Enter a commit message (e.g., 'Update to v1.1.0 with UI improvements and Zeno removal')"
    
    # Add all changes
    Write-Host "Adding all changes..." -ForegroundColor Cyan
    git add .
    
    # Commit changes
    Write-Host "Committing changes..." -ForegroundColor Cyan
    git commit -m $commitMessage
    
    Write-Host "Changes committed successfully!" -ForegroundColor Green
} else {
    Write-Host "No changes to commit." -ForegroundColor Green
}

# Push to GitHub
$branch = git branch --show-current
Write-Host "Current branch: $branch" -ForegroundColor Cyan

$pushConfirm = Read-Host "Do you want to push to GitHub? (y/n)"
if ($pushConfirm -eq "y") {
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push origin $branch
    Write-Host "Push completed!" -ForegroundColor Green
} else {
    Write-Host "Push cancelled." -ForegroundColor Yellow
}

Write-Host "`nBackup process completed!" -ForegroundColor Green
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
