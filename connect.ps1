# SSH Connection Script for Ubuntu Server
# Usage: .\connect.ps1

param(
    [string]$ConfigPath = ".\config.json"
)

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Error "SSH client not found. Please install OpenSSH Client or Git for Windows."
    exit 1
}

# Check if config file exists
if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath"
    exit 1
}

try {
    # Load configuration
    $config = Get-Content $ConfigPath | ConvertFrom-Json
    
    $hostname = $config.host
    $port = $config.port
    $user = $config.user
    $auth = $config.auth_method
    $keyPath = $config.key_path
    
    # Build SSH arguments
    $arguments = @()
    $arguments += "-p"; $arguments += $port
    
    # Add key authentication if specified
    if ($auth -eq "key" -and -not [string]::IsNullOrWhiteSpace($keyPath)) {
        if (-not (Test-Path -Path $keyPath)) {
            Write-Warning "Key file not found: $keyPath"
        } else {
            $arguments += "-i"; $arguments += $keyPath
        }
    }
    
    # Add connection target
    $arguments += "$user@$hostname"
    
    Write-Host "Connecting to: $user@$hostname (port $port)" -ForegroundColor Cyan
    & ssh @arguments
    
} catch {
    Write-Error "Failed to connect: $($_.Exception.Message)"
    exit 1
}