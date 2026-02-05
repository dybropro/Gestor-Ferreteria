; Script de Inno Setup para Ferreteria Dybro
; Este archivo configura la creación del instalador y protege la base de datos en las actualizaciones.

#define MyAppName "Ferreteria Dybro"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "DybroCorp"
#define MyAppExeName "FerreteriaDybro.exe"

[Setup]
; AppId debe ser el mismo en todas las versiones para que Windows reconozca las actualizaciones
AppId={{D1A3B5C7-8E92-4B2D-A5C3-63580C5AA964}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; --- CONTRASEÑA DEL INSTALADOR ---
; Esto hará que el instalador pida una contraseña antes de empezar
Password=DybroCorp2026
DisableProgramGroupPage=yes
OutputDir=setup_build
OutputBaseFilename=FerreteriaDybro_Instalador
SetupIconFile=logo_dybrocorp_dark.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
; Archivos del programa (generados con PyInstaller en la carpeta dist)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; --- PROTECCIÓN DE DATOS ---
; La bandera 'onlyifdoesntexist' evita que el instalador sobrescriba tu base de datos si ya existe.
; La bandera 'uninsneveruninstall' asegura que la DB no se borre al desinstalar (opcional).
Source: "ferreteria.db"; DestDir: "{app}"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
