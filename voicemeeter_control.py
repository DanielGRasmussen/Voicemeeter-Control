import logging
import os
import subprocess
import sys

from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject
import voicemeeter
import yaml

from hotkey_handler import HotkeyHandler
from volume_display import VolumeDisplay

# Toggle logging on/off
ENABLE_LOGGING = False

# Set up logging
if ENABLE_LOGGING:
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
		handlers=[
			logging.FileHandler("voicemeeter_controller.log"),
			logging.StreamHandler()
		]
	)
	logger = logging.getLogger(__name__)
else:
	class DummyLogger:
		"""Logger that does nothing when called"""
		def __getattr__(self, name):
			"""Accepts anything, does nothing"""
			return lambda *args, **kwargs: None

	logger = DummyLogger()


class NotificationSignals(QObject):
	"""
    Handles Qt signals for system notifications.
    Used to safely emit notification signals across threads. (I think)
    """
	show_notification = pyqtSignal(str)


class VoiceMeeterController:
	"""
    Main controller class for the VoiceMeeter application.
    Handles hotkey bindings, system tray integration, and VoiceMeeter interactions.
    
    Features:
		- Global hotkey support for controlling VoiceMeeter
		- System tray integration with context menu
		- Volume and mute controls for multiple channels
		- Visual notifications for volume/mute changes
		- Configurable via YAML file
		- Automatic VoiceMeeter connection management
		- Support for pausing/resuming hotkey listening
		- Application restart capability
    """
	def __init__(self, config_path):
		"""
        Initialize the VoiceMeeter controller with configuration.
        
        Args:
            config_path (str): Path to the YAML configuration file
        """
		self.keyboard_listener = None
		self.config = None
		self.settings = None
		self.app = QApplication(sys.argv)
		self.load_config(config_path)
		self.vm = voicemeeter.remote("potato")
		self.vm.login()

		self.paused = False

		# Set up notification system
		self.display = VolumeDisplay()
		self.notification_signals = NotificationSignals()
		self.notification_signals.show_notification.connect(
			self.display.show_notification
		)

		self.setup_hotkeys()

		# Create system tray
		self.tray = QSystemTrayIcon(QIcon("icon.png"))
		self.create_tray_menu()
		self.tray.show()

		logger.info("VoiceMeeter Controller initialized")

	def load_config(self, config_path):
		"""
        Load and parse the YAML configuration file.
        
        Args:
            config_path (str): Path to the configuration file
        """
		with open(config_path, "r") as f:
			self.config = yaml.safe_load(f)
		logger.info(f"Loaded configuration from {config_path}")

		self.settings = self.config["settings"]

	def create_tray_menu(self):
		"""
        Create and configure the system tray icon context menu.
        Adds pause, restart, and quit options.
        """
		menu = QMenu()
		pause_action = menu.addAction("Pause")
		pause_action.setCheckable(True)
		pause_action.triggered.connect(self.pause)
		restart_action = menu.addAction("Restart")
		restart_action.triggered.connect(self.restart)
		quit_action = menu.addAction("Quit")
		quit_action.triggered.connect(self.quit)
		self.tray.setContextMenu(menu)

	def pause(self):
		"""
        Toggle the paused state of the controller.
        When paused, hotkeys are temporarily disabled.
        """
		self.paused = not self.paused

	def restart(self):
		"""
        Restart the application by launching a new instance and terminating the current one.
        Preserves the console/windowless state of the current instance.
        """
		try:
			logger.info("Restarting Voicemeeter Control...")

			# Get the path to the current script
			script_path = os.path.abspath(sys.argv[0])
			python_exe = sys.executable

			# Start new instance
			if python_exe.endswith("pythonw.exe"):
				# If running as windowless, start new windowless instance
				subprocess.Popen([python_exe, script_path])
			else:
				# If running with console, preserve that
				subprocess.Popen([python_exe, script_path],
								 creationflags=subprocess.CREATE_NEW_CONSOLE)

			self.quit()

		except Exception as e:
			logging.error(f"Error during restart: {str(e)}")

	def quit(self):
		"""
        Clean up and terminate the application.
        Logs out of VoiceMeeter, stops the keyboard listener, and exits the Qt application.
        """
		self.vm.logout()
		self.keyboard_listener.stop()
		self.app.quit()
		logger.info("Application terminated")

	def setup_hotkeys(self):
		"""
        Configure global hotkeys based on the loaded configuration.
        Maps hotkeys to specific channels and actions (mute, volume up/down).
        Supports multiple modifier key combinations for each action.
        """
		hotkeys = {}

		# Iterate through each channel and its actions
		for channel, actions in self.config["hotkeys"].items():
			channel_index = self.config["channels"][channel]

			# Process each action type (mute, up, down)
			for action, keys in actions.items():
				# Convert single string to list for consistent processing
				key_list = keys if isinstance(keys, list) else [keys]

				# Add each hotkey to the mapping
				for key in key_list:
					# Process the key
					hotkey_split = key.split("+")
					main_key = hotkey_split.pop()
					modifiers = tuple(sorted(hotkey_split)) # Sort modifiers for consistent comparison

					# Create or update the mapping for this main key
					if main_key not in hotkeys:
						hotkeys[main_key] = []

					hotkeys[main_key].append({
						"modifiers": modifiers,
						"callback": self.handle_hotkey,
						"args": (channel, action, channel_index)
					})

		handler = HotkeyHandler(hotkeys)
		self.keyboard_listener = handler

	def handle_hotkey(self, channel, action, index):
		"""
        Process hotkey events and apply the corresponding action to VoiceMeeter.
        
        Args:
            channel (str): Name of the channel to modify
            action (str): Action to perform ('mute', 'up', or 'down')
            index (int): VoiceMeeter channel index
        """
		try:
			if self.vm.dirty:
				self.update()
			current_volume = self.vm.inputs[index].gain

			if action == "mute":
				new_state = not self.vm.inputs[index].mute
				self.vm.inputs[index].mute = new_state
				status = "Muted" if new_state else "Unmuted"
				self.notification_signals.show_notification.emit(f"{channel.title()}: {status}")
				logger.info(f"{channel} {status.lower()}")

			elif action == "up":
				new_volume = min(12.0, current_volume + self.settings["volume_step"])
				self.vm.inputs[index].gain = new_volume
				self.notification_signals.show_notification.emit(f"{channel.title()}: {new_volume:.1f} dB")
				logger.info(f"{channel} volume increased to {new_volume:.1f} dB")

			elif action == "down":
				new_volume = max(-60.0, current_volume - self.settings["volume_step"])
				self.vm.inputs[index].gain = new_volume
				self.notification_signals.show_notification.emit(f"{channel.title()}: {new_volume:.1f} dB")
				logger.info(f"{channel} volume decreased to {new_volume:.1f} dB")

		except Exception as e:
			logger.error(f"Error handling hotkey for {channel}: {str(e)}")

	def update(self):
		"""
        Update VoiceMeeter state. Ideally this shouldn't be hard coded and the config file should
		ask a throwaway setting.
        Any change updates all other info.
        """
		target = self.vm.inputs[4]
		target.mute = True


def main():
	"""
    Application entry point. Initialize and run the VoiceMeeter controller.
    Handles top-level exception logging and proper exit codes.
    """
	try:
		controller = VoiceMeeterController("config.yaml")
		sys.exit(controller.app.exec_())
	except Exception as e:
		logger.error(f"Application error: {str(e)}")
		sys.exit(1)


if __name__ == "__main__":
	main()
