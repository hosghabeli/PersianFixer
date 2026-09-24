; =====================================================================
; PersianFixer - Inno Setup Script
; Modern, Clean, User-Level Installer for Windows
; =====================================================================

#ifndef MyAppVersion
#define MyAppVersion "3.10.0"
#endif

#define MyAppName "PersianFixer"
#define MyAppPublisher "Hossein Gholami"
#define MyAppURL "https://github.com/hosgh/PersianFixer"
#define MyAppExeName "PersianFixer.vbs"

[Setup]
AppId={{D37E7A5A-4B28-44A9-9FE8-F5BE75069B88}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=PersianFixer-v{#MyAppVersion}-Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\icon.ico
ArchitecturesInstallIn64BitMode=x64compatible
VersionInfoVersion={#MyAppVersion}.0
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "autostart"; Description: "اجرا همراه با بالا آمدن ویندوز (Start with Windows)"; GroupDescription: "تنظیمات سیستمی:"; Flags: unchecked

[Files]
Source: "gui.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "patcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "font_installer.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "autostart.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "persian_engine.js"; DestDir: "{app}"; Flags: ignoreversion
Source: "asar_patcher.js"; DestDir: "{app}"; Flags: ignoreversion
Source: "apply_antigravity_patch.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "PersianFixer.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "run.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "package.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "node_modules\*"; DestDir: "{app}\node_modules"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "wscript.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Comment: "دستیار فارسی و فونت وزیرمتن برای ابزارهای هوش مصنوعی"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "wscript.exe ""{app}\{#MyAppExeName}"" --tray"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "wscript.exe"; Parameters: """{app}\{#MyAppExeName}"""; Description: "اجرای PersianFixer پس از اتمام نصب"; Flags: nowait postinstall skipifsilent
