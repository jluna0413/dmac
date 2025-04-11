# Start the PostgreSQL database and the DMac server
Write-Host "Starting DMac Server with PostgreSQL..." -ForegroundColor Green

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed. Please install Docker before proceeding." -ForegroundColor Red
    exit
}

# Start PostgreSQL using Docker Compose
Write-Host "Starting PostgreSQL..." -ForegroundColor Cyan
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Cyan
$ready = $false
$attempts = 0
$maxAttempts = 10

while (-not $ready -and $attempts -lt $maxAttempts) {
    $attempts++
    
    try {
        $health = docker inspect --format='{{.State.Health.Status}}' dmac-postgres
        
        if ($health -eq "healthy") {
            $ready = $true
            Write-Host "PostgreSQL is ready!" -ForegroundColor Green
        } else {
            Write-Host "PostgreSQL is not ready yet (Status: $health). Waiting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    } catch {
        Write-Host "Error checking PostgreSQL status. Waiting..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Host "PostgreSQL failed to start after $maxAttempts attempts. Please check the logs." -ForegroundColor Red
    exit
}

# Set the PostgreSQL connection string environment variable
$env:DMAC_DB_URL = "postgresql://postgres:postgres@localhost/dmac"

# Start the DMac server
Write-Host "Starting DMac server..." -ForegroundColor Cyan
python run_server.py

# Clean up
Write-Host "Server stopped. Cleaning up..." -ForegroundColor Cyan
docker-compose down

Write-Host "Done!" -ForegroundColor Green
