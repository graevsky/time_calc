$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCommand) {
    throw "Python 3 is required to install time_calc."
}

if (-not ("Win32.NativeMethods" -as [type])) {
    Add-Type @"
using System;
using System.Runtime.InteropServices;

namespace Win32 {
    public static class NativeMethods {
        [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
        public static extern IntPtr SendMessageTimeout(
            IntPtr hWnd,
            uint Msg,
            UIntPtr wParam,
            string lParam,
            uint fuFlags,
            uint uTimeout,
            out UIntPtr lpdwResult
        );
    }
}
"@
}

& $pythonCommand.Source -m pip install --user --no-build-isolation --upgrade $projectRoot

$scriptsDir = (& $pythonCommand.Source -c "import sysconfig; print(sysconfig.get_path('scripts', scheme=sysconfig.get_preferred_scheme('user')))").Trim()
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$userEntries = @()

if ($userPath) {
    $userEntries = $userPath.Split(';') | Where-Object { $_ }
}

if ($userEntries -notcontains $scriptsDir) {
    $newPath = if ($userPath) { "$userPath;$scriptsDir" } else { $scriptsDir }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $hwndBroadcast = [IntPtr]0xffff
    $wmSettingChange = 0x001A
    $sendMessageTimeoutFlags = 0x0002
    $result = [UIntPtr]::Zero
    [void][Win32.NativeMethods]::SendMessageTimeout(
        $hwndBroadcast,
        $wmSettingChange,
        [UIntPtr]::Zero,
        "Environment",
        $sendMessageTimeoutFlags,
        5000,
        [ref]$result
    )
    Write-Host "Added $scriptsDir to your user PATH."
    Write-Host "New terminal windows will see the updated PATH."
    Write-Host 'To refresh PATH in the current PowerShell session, run:'
    Write-Host '$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")'
} else {
    Write-Host "PATH already contains $scriptsDir."
}

Write-Host "Installed time_calc. Try: time_calc --help"
