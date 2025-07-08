"""
Voicemeeter Control Installation Builder Script
Creates a Windows installer using PyInstaller and Inno Setup
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Configuration
APP_NAME = "Voicemeeter Control"
APP_VERSION = "1.0.0"
APP_PUBLISHER = "Daniel Rasmussen"
APP_URL = "https://github.com/danielgrasmussen/voicemeeter-control"
APP_GUID = "{4285c7a1-b182-47b7-bfed-1fd7e7096f83}"

class InstallerBuilder:
    def __init__(self):
        # Determine safe working directory
        self.setup_working_directory()
        
    def setup_working_directory(self):
        """Setup a safe working directory for builds"""
        # Check if we're in Program Files (protected directory)
        current_dir = Path.cwd()
        program_files_paths = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
            Path(os.environ.get('PROGRAMW6432', 'C:\\Program Files'))
        ]
        
        in_protected_dir = any(
            str(current_dir).startswith(str(pf)) 
            for pf in program_files_paths 
            if pf.exists()
        )
        
        if in_protected_dir:
            # Use temp directory for builds
            print("⚠️  Detected protected directory, using temp folder for build...")
            self.root_dir = Path(tempfile.gettempdir()) / "VoicemeeterControl_Build"
            self.root_dir.mkdir(exist_ok=True)
            
            # Copy source files to temp directory
            print(f"📁 Working directory: {self.root_dir}")
            source_files = [
                'voicemeeter_control.py',
                'volume_display.py',
                'hotkey_handler.py',
                'config.yaml',
                'icon.png',
                'LICENSE',
                'README.md'
            ]
            
            for file in source_files:
                src = current_dir / file
                if src.exists():
                    shutil.copy2(src, self.root_dir / file)
                    print(f"  ✓ Copied {file}")
        else:
            # Use current directory
            self.root_dir = current_dir
            
        # Create build folders
        self.build_folder = self.root_dir / "build_output"
        self.build_folder.mkdir(exist_ok=True)
        
        # Setup subdirectories
        self.dist_dir = self.build_folder / "dist"
        self.build_dir = self.build_folder / "build"
        self.installer_dir = self.build_folder / "installer"
        self.temp_dir = self.build_folder / "temp"
        
        # Create all directories
        for directory in [self.dist_dir, self.build_dir, self.installer_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True)
            
        print(f"\n📂 Build output folder: {self.build_folder}")
        
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("\n🧹 Cleaning build directories...")
        for dir_path in [self.dist_dir, self.build_dir, self.temp_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                dir_path.mkdir(exist_ok=True)
        
    def create_spec_file(self):
        """Create PyInstaller spec file"""
        print("\n📝 Creating PyInstaller spec file...")
        
        # Convert paths to use forward slashes to avoid escape sequence issues
        root_dir_str = str(self.root_dir).replace('\\', '/')
        temp_dir_str = str(self.temp_dir).replace('\\', '/')
        build_folder_str = str(self.build_folder).replace('\\', '/')
        
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{root_dir_str}/voicemeeter_control.py'],
    pathex=['{root_dir_str}'],
    binaries=[],
    datas=[
        ('{root_dir_str}/config.yaml', '.'),
        ('{root_dir_str}/icon.png', '.'),
        ('{root_dir_str}/README.md', '.'),
        ('{root_dir_str}/LICENSE', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'yaml',
        'voicemeeter',
        'voicemeeter.remote',
        'keyboard',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME.replace(" ", "")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='{temp_dir_str}/version_info.txt',
    icon='{build_folder_str}/icon.ico',
    uac_admin=False,
)
'''
        
        spec_file = self.temp_dir / 'voicemeeter_control.spec'
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        print(f"  ✓ Created: {spec_file}")
        return spec_file
    
    def create_version_info(self):
        """Create version info file for Windows executable"""
        print("\n📋 Creating version info...")
        
        version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{APP_PUBLISHER}'),
        StringStruct(u'FileDescription', u'Voicemeeter Control - Global hotkeys for Voicemeeter'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 {APP_PUBLISHER}'),
        StringStruct(u'OriginalFilename', u'{APP_NAME.replace(" ", "")}.exe'),
        StringStruct(u'ProductName', u'{APP_NAME}'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.temp_dir / 'version_info.txt'
        with open(version_file, 'w') as f:
            f.write(version_info)
        print(f"  ✓ Created: {version_file}")
    
    def build_exe(self, spec_file):
        """Build executable with PyInstaller"""
        print("\n🔨 Building executable with PyInstaller...")
        
        # Change to root directory for build
        original_dir = os.getcwd()
        os.chdir(self.root_dir)
        
        try:
            # First ensure PyInstaller is installed
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         capture_output=True, check=True)
            
            # Build the executable with custom paths
            result = subprocess.run([
                "pyinstaller",
                "--clean",
                "--distpath", str(self.dist_dir),
                "--workpath", str(self.build_dir),
                str(spec_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Build failed:\n{result.stderr}")
                raise Exception("PyInstaller build failed")
            else:
                print("  ✓ Executable built successfully")
                
                # Copy icon.png to dist folder for the installer
                icon_src = self.root_dir / "icon.png"
                icon_dst = self.dist_dir / "icon.png"
                if icon_src.exists():
                    shutil.copy2(icon_src, icon_dst)
                    print("  ✓ Copied icon.png to dist folder")
                
        finally:
            os.chdir(original_dir)
    
    def create_inno_setup_script(self):
        """Create Inno Setup script for installer"""
        print("\n📦 Creating Inno Setup script...")
        
        # Convert paths for Inno Setup (uses Windows paths but doesn't have escape issues)
        root_dir_str = str(self.root_dir)
        dist_dir_str = str(self.dist_dir)
        build_folder_str = str(self.build_folder)
        exe_name = APP_NAME.replace(" ", "")
        
        inno_script = f'''
#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{APP_PUBLISHER}"
#define MyAppURL "{APP_URL}"
#define MyAppExeName "{exe_name}.exe"

[Setup]
AppId={{{APP_GUID}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{localappdata}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile={root_dir_str}\\LICENSE
OutputDir={build_folder_str}\\installer_output
OutputBaseFilename=VoicemeeterControl_Setup_v{{#MyAppVersion}}
SetupIconFile={build_folder_str}\\icon.ico
UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "{dist_dir_str}\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{dist_dir_str}\\icon.png"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{dist_dir_str}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{root_dir_str}\\config.yaml"; DestDir: "{{app}}"; Flags: onlyifdoesntexist

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{{app}}\\config.yaml"
Type: files; Name: "{{app}}\\*.log"

[Code]
function InitializeSetup(): Boolean;
var
  Message: string;
begin
  Result := True;
  
  // Check if Voicemeeter is installed by looking for common installation paths
  if not FileExists(ExpandConstant('{{pf}}\\VB\\Voicemeeter\\voicemeeter.exe')) and
     not FileExists(ExpandConstant('{{pf64}}\\VB\\Voicemeeter\\voicemeeter.exe')) and
     not FileExists(ExpandConstant('{{pf}}\\VB\\Voicemeeter Banana\\VoicemeeterBanana.exe')) and
     not FileExists(ExpandConstant('{{pf64}}\\VB\\Voicemeeter Banana\\VoicemeeterBanana.exe')) and
     not FileExists(ExpandConstant('{{pf}}\\VB\\Voicemeeter Potato\\VoicemeeterPotato.exe')) and
     not FileExists(ExpandConstant('{{pf64}}\\VB\\Voicemeeter Potato\\VoicemeeterPotato.exe')) then
  begin
    Message := 'Voicemeeter does not appear to be installed on this system.' + #13#10 + #13#10 +
               'This application requires Voicemeeter (Basic, Banana, or Potato) to function properly.' + #13#10 + #13#10 +
               'Would you like to continue with the installation anyway?';
    
    if MsgBox(Message, mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks
  end;
end;
'''
        
        setup_file = self.installer_dir / 'setup.iss'
        with open(setup_file, 'w') as f:
            f.write(inno_script)
        print(f"  ✓ Created: {setup_file}")
    
    def create_readme(self):
        """Create README.md if it doesn't exist"""
        readme_file = self.root_dir / 'README.md'
        if not readme_file.exists():
            print("\n📄 Creating README.md...")
            readme_content = f"""# Voicemeeter Control

Global hotkey control for Voicemeeter with visual notifications.

## Features

- 🎮 **Global Hotkeys** - Control Voicemeeter from any application
- 🔊 **Volume Control** - Adjust volume levels with keyboard shortcuts
- 🔇 **Mute Toggle** - Quick mute/unmute for any channel
- 📊 **Visual Feedback** - On-screen notifications for all actions
- ⚙️ **Customizable** - Configure hotkeys via YAML file
- 🔄 **Auto-repeat** - Hold keys for continuous adjustment

## Requirements

- Windows 10/11 (64-bit)
- Voicemeeter (Basic, Banana, or Potato)
- Python 3.8+ (if running from source)

## Installation

1. Install Voicemeeter from https://vb-audio.com/Voicemeeter/
2. Run the {APP_NAME} installer
3. Configure your hotkeys in config.yaml

## Configuration

Edit `config.yaml` to customize your hotkeys:

```yaml
settings:
  volume_step: 2.0
  logging: True

channels:
  microphone: 0
  desktop: 5
  music: 6
  voicechat: 7

hotkeys:
  microphone:
    mute: "print screen"
    up: "ctrl+f14"
    down: "ctrl+f15"
```

## Usage

1. Start {APP_NAME} - it will minimize to system tray
2. Use your configured hotkeys to control Voicemeeter
3. Right-click the tray icon for options

## Author

{APP_PUBLISHER}

## License

MIT License - see LICENSE file for details
"""
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            print(f"  ✓ Created: {readme_file}")
    
    def convert_icons(self):
        """Convert PNG icons to ICO format"""
        print("\n🎨 Converting icon...")
        
        try:
            from PIL import Image
            
            png_file = self.root_dir / 'icon.png'
            if png_file.exists():
                img = Image.open(png_file)
                ico_file = self.build_folder / 'icon.ico'
                img.save(ico_file, format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
                print(f"  ✓ Converted icon.png to icon.ico")
            else:
                print(f"  ⚠️  icon.png not found, creating placeholder...")
                # Create placeholder with VM initials
                img = Image.new('RGBA', (256, 256), (64, 64, 64, 255))
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                # Try to draw "VM" text
                try:
                    draw.text((128, 128), "VM", fill=(255, 255, 255, 255), anchor="mm")
                except:
                    pass
                png_file = self.build_folder / 'icon.png'
                img.save(png_file)
                ico_file = self.build_folder / 'icon.ico'
                img.save(ico_file, format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
                    
        except Exception as e:
            print(f"  ⚠️  Could not convert icon: {e}")
            print("     Please convert manually or use existing ICO file")
    
    def build_installer(self):
        """Main build process"""
        print(f"\n🚀 Building {APP_NAME} Installer v{APP_VERSION}")
        print("=" * 50)
        
        # Check for required files
        required_files = ['voicemeeter_control.py', 'volume_display.py', 
                         'hotkey_handler.py', 'config.yaml', 'LICENSE']
        missing_files = []
        
        for file in required_files:
            if not (self.root_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print("\n❌ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            print("\nPlease ensure these files exist before building.")
            return False
        
        try:
            # Step 1: Clean
            self.clean_build_dirs()
            
            # Step 2: Create necessary files
            self.create_readme()
            self.create_version_info()
            self.convert_icons()
            
            # Step 3: Create spec and build executable
            spec_file = self.create_spec_file()
            self.build_exe(spec_file)
            
            # Step 4: Create installer script
            self.create_inno_setup_script()
            
            # Create installer output directory
            installer_output = self.build_folder / "installer_output"
            installer_output.mkdir(exist_ok=True)
            
            print("\n" + "=" * 50)
            print("✅ Build complete!")
            print(f"\n📁 All build files are in: {self.build_folder}")
            exe_name = APP_NAME.replace(" ", "")
            print(f"   • Executable: {self.dist_dir / f'{exe_name}.exe'}")
            print(f"   • Installer script: {self.installer_dir / 'setup.iss'}")
            print("\n📌 Next steps:")
            print("   1. Install Inno Setup from https://jrsoftware.org/isdl.php")
            print(f"   2. Open {self.installer_dir / 'setup.iss'} in Inno Setup")
            print("   3. Press F9 to compile the installer")
            print(f"   4. Find installer in: {installer_output}")
            
            # If we used temp directory, offer to open it
            if self.root_dir != Path.cwd():
                print(f"\n💡 Tip: Build folder will open automatically...")
                os.startfile(self.build_folder)
                
        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True


if __name__ == "__main__":
    builder = InstallerBuilder()
    success = builder.build_installer()
    
    # Exit with proper error code
    sys.exit(0 if success else 1)