# Arduino Soundbar - Installer/Updater (User-mode, no admin required)
# - Prompts for install path (default: Documents\Arduino Soundbar)
# - Downloads latest GitHub release asset (ArduinoSoundbar-win64.zip)
# - Extracts to install folder (overwrites files)
# - Preserves existing config.json if present
# - Creates/updates a Desktop shortcut

$ErrorActionPreference = "Stop"

# ================== CONFIG ==================
$Owner      = "YaBraG"
$Repo       = "Arduino-Soundbar"
$AssetName  = "ArduinoSoundbar-win64.zip"
$AppName    = "Arduino Soundbar"
$ExeName    = "Soundbar.exe"
$ConfigName = "config.json"
# ===========================================

function Write-Info($msg) { Write-Host "[INFO] $msg" }
function Write-OK($msg)   { Write-Host "[OK]   $msg" }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" }

function Read-InstallPath($defaultPath) {
    Write-Host ""
    Write-Host "Choose install folder (press ENTER for default):"
    Write-Host "Default: $defaultPath"
    $input = Read-Host "Install path"

    if ([string]::IsNullOrWhiteSpace($input)) {
        return $defaultPath
    }

    $expanded = [Environment]::ExpandEnvironmentVariables($input).Trim()

    # If user typed relative path, interpret it relative to user profile
    if (-not [System.IO.Path]::IsPathRooted($expanded)) {
        $expanded = Join-Path $env:USERPROFILE $expanded
    }

    return $expanded
}

try {
    # 1) Choose install directory (Documents\Arduino Soundbar default)
    $documents = [Environment]::GetFolderPath("MyDocuments")
    $defaultInstallDir = Join-Path $documents $AppName
    $installDir = Read-InstallPath $defaultInstallDir

    Write-Info "Installing to: $installDir"

    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir | Out-Null
        Write-OK "Created install folder."
    }

    # 2) Query latest release
    $api = "https://api.github.com/repos/$Owner/$Repo/releases/latest"
    Write-Info "Fetching latest release info..."
    $release = Invoke-RestMethod -Uri $api -Headers @{ "User-Agent" = "$AppName-Installer" }

    Write-Info "Latest release tag: $($release.tag_name)"

    $asset = $release.assets | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1
    if (-not $asset) {
        throw "Could not find asset named '$AssetName' in the latest release."
    }

    $downloadUrl = $asset.browser_download_url
    Write-Info "Downloading: $downloadUrl"

    # 3) Download ZIP to temp
    $tempZip = Join-Path $env:TEMP $AssetName
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip
    Write-OK "Downloaded release zip."

    # 4) Preserve existing config.json (if user already installed once)
    $existingConfig = Join-Path $installDir $ConfigName
    $backupConfig   = $null

    if (Test-Path $existingConfig) {
        $backupConfig = Join-Path $env:TEMP ("$ConfigName.backup")
        Copy-Item $existingConfig $backupConfig -Force
        Write-Info "Backed up existing config.json (will restore after update)."
    }

    # 5) Extract zip into install folder
    Write-Info "Extracting zip..."
    Expand-Archive -Path $tempZip -DestinationPath $installDir -Force
    Remove-Item $tempZip -Force
    Write-OK "Extracted files to install folder."

    # 6) Restore config.json if it existed
    if ($backupConfig -and (Test-Path $backupConfig)) {
        Copy-Item $backupConfig $existingConfig -Force
        Remove-Item $backupConfig -Force
        Write-OK "Restored existing config.json (preserved user settings)."
    }

    # 7) Verify exe exists
    $exePath = Join-Path $installDir $ExeName
    if (-not (Test-Path $exePath)) {
        throw "Install failed: '$ExeName' not found in $installDir. (Check your zip contents.)"
    }
    Write-OK "Found $ExeName."

    # 8) Create Desktop shortcut
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "$AppName.lnk"

    $wsh = New-Object -ComObject WScript.Shell
    $sc = $wsh.CreateShortcut($shortcutPath)
    $sc.TargetPath = $exePath
    $sc.WorkingDirectory = $installDir
    $sc.IconLocation = $exePath
    $sc.Save()

    Write-OK "Desktop shortcut created: $shortcutPath"
    Write-OK "Install/Update complete. Launch from the Desktop shortcut."

} catch {
    Write-Err $_.Exception.Message
    Write-Host ""
    Write-Host "If you got 'asset not found', confirm your release has an asset named exactly: $AssetName"
    Write-Host "If you got 'exe not found', confirm the zip contains: $ExeName at the TOP LEVEL (no folders)."
}
