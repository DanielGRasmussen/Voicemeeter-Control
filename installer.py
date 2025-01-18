import os
import subprocess
import sys
import shutil
import winreg
from pathlib import Path
import ctypes
import logging
from datetime import datetime

def is_admin():
	try:
		return ctypes.windll.shell32.IsUserAnAdmin()
	except:
		return False

def setup_logging():
	log_path = Path("installer_log.log")
	logging.basicConfig(
		filename=log_path,
		level=logging.INFO,
		format='%(asctime)s - %(levelname)s - %(message)s'
	)

def create_batch_file(install_dir):
	batch_content = """@echo off
start "" /b "C:\\Python311\\pythonw.exe" "C:\\Program Files\\Voicemeeter Macros\\voicemeeter_control.py"
if errorlevel 1 (
	echo Error starting VoicemeeterControl >> "C:\\Program Files\\Voicemeeter Macros\\startup_error.log"
	exit /b 1
)"""
	
	batch_path = install_dir / "start_voicemeeter_control.bat"
	try:
		with open(batch_path, 'w') as f:
			f.write(batch_content)
		logging.info(f"Created batch file at {batch_path}")
	except Exception as e:
		logging.error(f"Failed to create batch file: {e}")
		raise

def create_vbs_file(install_dir):
	key = winreg.OpenKey(
		winreg.HKEY_CURRENT_USER,
		r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
		0, winreg.KEY_READ
	)
	startup_folder = Path(winreg.QueryValueEx(key, "Startup")[0])
	print(startup_folder)

	vbs_content = f'''Set WShell = CreateObject("WScript.Shell")
On Error Resume Next
WShell.Run """{install_dir / "start_voicemeeter_control.bat"}""", 0, False
If Err.Number <> 0 Then
	With CreateObject("Scripting.FileSystemObject")
		.OpenTextFile("{startup_folder}\\vm_control_error.log", 8, True).WriteLine(Now & " - Error: " & Err.Description)
	End With
End If'''
	vbs_path = startup_folder / "Voicemeeter Macros.vbs"
	vbs_path.write_text(vbs_content, encoding='utf-8')

	return vbs_path

def main():


	# Setup logging
	setup_logging()
	
	# Check for admin privileges
	if not is_admin():
		logging.error("Script must be run with administrator privileges")
		ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
		sys.exit(1)

	try:
		# Define paths
		current_dir = Path.cwd()
		install_dir = Path("C:/Program Files/Voicemeeter Macros")
		
		# Create installation directory if it doesn't exist
		install_dir.mkdir(parents=True, exist_ok=True)
		logging.info(f"Created installation directory: {install_dir}")

		# Files to install (add your specific files here)
		files_to_install = [
			"voicemeeter_control.py",
			"hotkey_handler.py",
			"volume_display.py",
			"icon.png",
			"config.yaml"
		]

		# Copy files
		for file in files_to_install:
			source = current_dir / file
			destination = install_dir / file
			
			if not source.exists():
				logging.error(f"Source file not found: {source}")
				raise FileNotFoundError(f"Required file not found: {file}")
				
			shutil.copy2(source, destination)
			logging.info(f"Copied {file} to {destination}")

		create_batch_file(install_dir)
		vbs_path = create_vbs_file(install_dir)
		
		print("Installation completed successfully!")
		logging.info("Installation completed successfully")

		subprocess.run(["wscript", vbs_path], check=True)
		
	except Exception as e:
		logging.error(f"Installation failed: {e}")
		print(f"Installation failed. Check installer_log.log for details.")
		sys.exit(1)

if __name__ == "__main__":
	main()