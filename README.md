HEIC to JPEG Converter

This small GUI program converts .HEIC files to .JPG only when a matching .jpg doesn't already exist in the output folder.

Quick start (Windows):

1. Install Python 3.8+ and ensure `python` is on PATH.
2. From this folder, install dependencies and build an exe using the bundled script:

   Open PowerShell in this folder and run:

   .\build_exe.ps1

3. After the build completes, the single-file executable will be in the `dist` directory (named `heic_to_jpeg.exe` by default).

Notes and caveats:
- The program uses `pillow-heif` to read HEIC images; that package can require additional binary dependencies on some platforms. If the exe fails to load HEIC images, install `libheif`/system libs or run the script with a Python environment where `pillow_heif` works.
- The generated exe uses PyInstaller's onefile mode. If you see runtime errors due to missing data files, we can add explicit `--add-data` flags.
- The GUI will default to the drive where the script was located for input/output (e.g. D:\folder_heic).

If you want, I can refine the build script to create a virtualenv first, pin exact package versions, or produce an installer (MSI/NSIS).
