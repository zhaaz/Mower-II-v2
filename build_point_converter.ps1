$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtuelle Umgebung nicht gefunden: $python"
}

Write-Host "Installiere bzw. aktualisiere PyInstaller..."
& $python -m pip install --upgrade pyinstaller

Write-Host "Erstelle Mower Point Converter..."
$pyInstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", "MowerPointConverter",
    "--paths", (Join-Path $projectRoot "src"),
    (Join-Path $projectRoot "src\mower\tools\point_converter_app.py")
)
& $python -m PyInstaller @pyInstallerArgs

$exe = Join-Path $projectRoot "dist\MowerPointConverter\MowerPointConverter.exe"
if (-not (Test-Path $exe)) {
    throw "Build abgeschlossen, EXE wurde aber nicht gefunden: $exe"
}

Write-Host ""
Write-Host "Fertig: $exe" -ForegroundColor Green
