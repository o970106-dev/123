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
    $raw_config = Get-Content $ConfigPath | ConvertFrom-Json

    # 支持嵌套或扁平結構
    if ($null -ne $raw_config.ssh) {
        $config = $raw_config.ssh
    } else {
        $config = $raw_config
    }
    
    $hostname = $config.host
    $port = $config.port
    $user = $config.user
    $auth = $config.auth_method
    $keyPath = $config.key_path
    
    # 檢查必要欄位
    if ([string]::IsNullOrWhiteSpace($hostname) -or [string]::IsNullOrWhiteSpace($user) -or $hostname -eq "your.server.ip") {
        Write-Error "Invalid config: host and user are required and should not be placeholders."
        exit 1
    }

    # Build SSH arguments
    $arguments = @()
    if ($null -ne $port) {
        $arguments += "-p"; $arguments += $port
    } else {
        $arguments += "-p"; $arguments += 22
    }
    
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
    
    Write-Host "Connecting to: $user@$hostname (port $($port -or 22))" -ForegroundColor Cyan
    & ssh @arguments
    
} catch {
    Write-Error "Failed to connect: $($_.Exception.Message)"
    exit 1
}
