[Setup]
AppName=EfiritPluginWebServer
AppVersion=1.0
DefaultDirName={pf}\EfiritPluginWebServer
DefaultGroupName=EfiritPluginWebServer
OutputDir=Output
OutputBaseFilename=EfiritPluginWebServerSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "server\main.py"; DestDir: "{app}"
Source: "server\uvicorn_server.py"; DestDir: "{app}"
Source: "server\drivers\atol10.py"; DestDir: "{app}server\drivers"
Source: "server\schemas\settings.py"; DestDir: "{app}server\schemas"
Source: "server\schemas\kkt.py"; DestDir: "{app}server\schemas"
Source: "server\schemas\exceptions.py"; DestDir: "{app}server\schemas"
Source: "server\models\atol_device.py"; DestDir: "{app}server\models"
Source: "server\models\base.py"; DestDir: "{app}server\models"
Source: "dist\main.exe"; DestDir: "{app}dist"
Source: "main.py"; DestDir: "{app}"
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "1.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "3.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "4.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\EfiritPluginWebServer"; Filename: "{app}\main.py"
Name: "{group}\Uninstall EfiritPluginWebServer"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\python.exe"; Parameters: "main.py"; WorkingDir: "{app}"; Description: "Run EfiritPluginWebServer"; Flags: postinstall skipifsilent