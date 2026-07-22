@echo off
echo Building Aeterna Roma Standalone Application...
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /target:winexe /out:AeternaRoma.exe /r:System.dll /r:System.Core.dll /r:System.Web.dll /r:System.Web.Extensions.dll /r:System.Windows.Forms.dll /r:System.Drawing.dll Program.cs GameModel.cs CombatEngine.cs SaveManager.cs WebAssets.cs Server.cs
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] AeternaRoma.exe compiled successfully!
) else (
    echo [ERROR] Compilation failed.
)
