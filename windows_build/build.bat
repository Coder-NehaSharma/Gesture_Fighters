@echo off
echo Building Gesture Fighter Client for Windows...
echo.

:: 1. Install PyInstaller
pip install pyinstaller

:: 2. Build Exe
:: --onefile: Bundle everything into one .exe
:: --noconsole: Hide the black terminal window (remove if you want to see errors)
:: --add-data: MediaPipe sometimes needs binary data, but 'mediapipe' package usually handles it. 
::             If it crashes, we might need a hook.

pyinstaller --onefile --name "GestureClient" ..\client_capture.py

echo.
echo Build Complete!
echo Look for 'GestureClient.exe' in the 'dist' folder.
echo.
pause
