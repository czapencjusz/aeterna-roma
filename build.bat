@echo off
echo Building Aeterna Roma launcher...
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
if not exist "%CSC%" set CSC=C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe
if not exist "%CSC%" (
    echo [ERROR] Could not find the .NET Framework 4 C# compiler ^(csc.exe^).
    exit /b 1
)
"%CSC%" /nologo /target:winexe /out:AeternaRoma.exe /r:System.dll /r:System.Windows.Forms.dll /resource:game.html,AeternaRoma.game.html Program.cs
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] AeternaRoma.exe compiled successfully!
) else (
    echo [ERROR] Compilation failed.
    exit /b 1
)
