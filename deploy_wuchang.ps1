<#
One-click deploy for Nginx + Certbot on the VM.
Reads SSH settings from config.json in the same folder.

Steps:
- Upload nginx_wuchang.life.conf and www_redirect_443.conf
- Enable site, test, reload
- Install Certbot and issue certs for all domains with redirect
- Enable 443 www->root redirect, test, reload
#>

param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$confMain = Join-Path $root 'nginx_wuchang.life.conf'
$confWww443 = Join-Path $root 'www_redirect_443.conf'
$configPath = Join-Path $root 'config.json'

if (!(Test-Path $configPath)) {
  throw "Missing config.json at $configPath"
}

$cfg = Get-Content -Raw -Path $configPath | ConvertFrom-Json
foreach ($key in 'host','user','port','key_path') {
  if (-not $cfg.$key) { throw "config.json missing '$key'" }
}

if (!(Test-Path $cfg.key_path)) {
  throw "SSH key not found: $($cfg.key_path)"
}

$sshTarget = "$($cfg.user)@$($cfg.host)"
$sshKey = $cfg.key_path

function Invoke-Remote {
  param([string]$cmd)
  Write-Host "[ssh] $cmd" -ForegroundColor Cyan
  & ssh -i $sshKey -p $($cfg.port) $sshTarget $cmd
}

Write-Host "Uploading Nginx configs to /tmp (then moving with sudo)..." -ForegroundColor Green
& scp -i $sshKey -P $($cfg.port) "$confMain" "${sshTarget}:/tmp/wuchang.life.conf"
& scp -i $sshKey -P $($cfg.port) "$confWww443" "${sshTarget}:/tmp/www_redirect_443.conf"

Write-Host "Placing main config into /etc/nginx and enabling site..." -ForegroundColor Green
Invoke-Remote "sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled"
Invoke-Remote "sudo mv /tmp/wuchang.life.conf /etc/nginx/sites-available/wuchang.life.conf"
Invoke-Remote "sudo ln -sf /etc/nginx/sites-available/wuchang.life.conf /etc/nginx/sites-enabled/wuchang.life.conf"
Invoke-Remote "sudo rm -f /etc/nginx/sites-enabled/www_redirect_443.conf"
Invoke-Remote "sudo nginx -t"
Invoke-Remote "sudo systemctl reload nginx"

Write-Host "Installing Certbot and issuing certificates..." -ForegroundColor Green
Invoke-Remote "sudo apt-get update"
Invoke-Remote "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx"

# Issue certs for all domains with automatic HTTP->HTTPS redirect
Invoke-Remote "sudo certbot --nginx -d wuchang.life -d www.wuchang.life -d bp.wuchang.life -d pos.bp.wuchang.life --redirect --non-interactive --agree-tos -m admin@wuchang.life || true"

Write-Host "Verifying certificate presence; fallback to self-signed if missing..." -ForegroundColor Green
$certStatus = Invoke-Remote "if [ -f /etc/letsencrypt/live/wuchang.life/fullchain.pem ] && [ -f /etc/letsencrypt/live/wuchang.life/privkey.pem ]; then echo HAVE_CERT; else echo NO_CERT; fi"
if (-not ($certStatus -match 'HAVE_CERT')) {
  Write-Warning "Let's Encrypt cert not present yet. Creating temporary self-signed cert (valid 7 days)."
  Invoke-Remote "sudo mkdir -p /etc/ssl/selfsigned /etc/letsencrypt/live/wuchang.life"
  Invoke-Remote "sudo openssl req -x509 -nodes -newkey rsa:2048 -days 7 -keyout /etc/ssl/selfsigned/wuchang.life.key -out /etc/ssl/selfsigned/wuchang.life.crt -subj '/CN=wuchang.life'"
  # Link self-signed certs to the expected Let's Encrypt paths
  Invoke-Remote "sudo ln -sf /etc/ssl/selfsigned/wuchang.life.crt /etc/letsencrypt/live/wuchang.life/fullchain.pem"
  Invoke-Remote "sudo ln -sf /etc/ssl/selfsigned/wuchang.life.key /etc/letsencrypt/live/wuchang.life/privkey.pem"
}

Write-Host "Final Nginx test and reload..." -ForegroundColor Green
Invoke-Remote "sudo nginx -t"
Invoke-Remote "sudo systemctl reload nginx"

# Now enable HTTPS www->root redirect after certs exist
Write-Host "Enabling HTTPS www->root redirect and reloading..." -ForegroundColor Green
Invoke-Remote "sudo mv /tmp/www_redirect_443.conf /etc/nginx/sites-available/www_redirect_443.conf"
Invoke-Remote "sudo ln -sf /etc/nginx/sites-available/www_redirect_443.conf /etc/nginx/sites-enabled/www_redirect_443.conf"
Invoke-Remote "sudo nginx -t"
Invoke-Remote "sudo systemctl reload nginx"

Write-Host "Done. Suggested remote checks:" -ForegroundColor Green
"- curl -I http://wuchang.life   (301 to https)"
"- curl -I http://www.wuchang.life (301 to https://wuchang.life)"
"- curl -I https://wuchang.life   (200/304)"
"- curl -I https://pos.bp.wuchang.life (200/304)"
"- curl -I https://bp.wuchang.life (403)"
