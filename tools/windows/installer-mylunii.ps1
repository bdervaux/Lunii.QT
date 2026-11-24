# Installe MyLunii sur ce PC Windows (sans droits administrateur) :
#   1. debloque les fichiers telecharges (sinon Windows les bloque),
#   2. copie MyLunii dans  %LOCALAPPDATA%\Programs\MyLunii,
#   3. cree les raccourcis sur le Bureau et dans le menu Demarrer,
#   4. ouvre MyLunii.
# Python n'est PAS necessaire : MyLunii.exe contient deja tout.
#
# Dans PowerShell :  powershell -ExecutionPolicy Bypass -File ".\installer-mylunii.ps1"
# Pour desinstaller : ajoutez  -Desinstaller  a la fin de la commande.
param([switch]$Desinstaller)

$ErrorActionPreference = 'Stop'
$here  = Split-Path -Parent $MyInvocation.MyCommand.Path
$src   = Join-Path $here 'MyLunii'
$dest  = Join-Path $env:LOCALAPPDATA 'Programs\MyLunii'
$exe   = Join-Path $dest 'MyLunii.exe'
$desktopLink = Join-Path ([Environment]::GetFolderPath('Desktop'))  'MyLunii.lnk'
$startLink   = Join-Path ([Environment]::GetFolderPath('Programs')) 'MyLunii.lnk'

function Step($text) { Write-Host ""; Write-Host "> $text" -ForegroundColor Magenta }
function Fail($text) { Write-Host ""; Write-Host "X $text" -ForegroundColor Red; Write-Host ""; exit 1 }

# fermer MyLunii s'il tourne (sinon ses fichiers sont verrouilles)
Get-Process -Name 'MyLunii' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

if ($Desinstaller) {
    Step "Desinstallation de MyLunii..."
    Remove-Item $desktopLink, $startLink -Force -ErrorAction SilentlyContinue
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Write-Host "  MyLunii est desinstalle. Votre bibliotheque d'histoires (dossier « Bibliothèque Lunii ») est conservee."
    exit 0
}

if (-not (Test-Path (Join-Path $src 'MyLunii.exe'))) {
    Fail "Le dossier « MyLunii » est introuvable : gardez ce script a cote de lui (decompressez tout le zip)."
}

Step "Deblocage des fichiers (securite Windows)..."
Get-ChildItem -Path $here -Recurse -File | Unblock-File -ErrorAction SilentlyContinue

Step "Installation de MyLunii dans $dest ..."
try {
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
    Copy-Item -Path $src -Destination $dest -Recurse -Force
} catch {
    Fail "Copie impossible : $($_.Exception.Message)"
}

Step "Creation des raccourcis (Bureau et menu Demarrer)..."
$shell = New-Object -ComObject WScript.Shell
foreach ($link in @($desktopLink, $startLink)) {
    $s = $shell.CreateShortcut($link)
    $s.TargetPath = $exe
    $s.WorkingDirectory = $dest
    $s.IconLocation = "$exe,0"
    $s.Description = 'MyLunii - par dervø'
    $s.Save()
}

Step "C'est pret ! MyLunii s'ouvre."
Write-Host "  Ensuite : double-cliquez sur « MyLunii » sur le Bureau ou cherchez-le dans le menu Demarrer."
Start-Process -FilePath $exe -WorkingDirectory $dest
