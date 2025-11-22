# Build script to create a single-file Windows executable using PyInstaller
# Usage: Open PowerShell in this folder and run: .\build_exe.ps1

param(
    [string]$script = "heic_to_jpeg.py",
    [string]$distName = "heic_to_jpeg"
)

# Ensure we're in the script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

Write-Host "Installing requirements (into current environment)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Building single-file executable with PyInstaller (using the active Python interpreter)..."
# Prefer running PyInstaller via the same python used to install packages so we don't rely on Scripts being on PATH
# --onefile produces a single EXE, --noconfirm overwrites, --add-data for pillow_heif (if needed) can be added
python -m PyInstaller --onefile --noconfirm --name $distName $script

Write-Host "Build finished. Find the executable in the 'dist' folder."
