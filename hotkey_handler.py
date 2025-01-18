import logging
import time

import keyboard

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

class HotkeyHandler:
	"""
	A keyboard hotkey manager that supports multiple modifier key combinations with repeat 
	functionality.

	This class provides a system for binding keyboard shortcuts to actions, supporting multiple
	modifier keys (Ctrl, Alt, Shift) in various combinations. It includes features for initial
	key press handling, key repeat with customizable delays, and automatic cleanup of keyboard
	listeners.

	Features:
		- Support for multiple modifier combinations (Ctrl, Alt, Shift)
		- Customizable repeat delay and interval
		- Automatic suppression of original key events
		- Clean handling of key state management

	Example:
		hotkey_actions = {
			'up': [
				{
					'modifiers': ('ctrl', 'shift'),
					'callback': some_function,
					'args': (1, 2),
					'kwargs': {'param': 'value'}
				}
			]
		}
		handler = HotkeyHandler(hotkey_actions, repeat_delay=0.5, repeat_interval=0.1)
	"""
	def __init__(self, hotkey_actions, repeat_delay=0.5, repeat_interval=0.1):
		"""
		Initialize hotkey handler with support for multiple modifier combinations

		Args:
			hotkey_actions (dict): A dictionary mapping main keys to lists of action dictionaries.
				Each action dictionary must contain:
				- modifiers (tuple): Required modifier keys ('ctrl', 'alt', 'shift')
				- callback (callable): Function to execute when hotkey is triggered
				- args (tuple): Positional arguments for the callback
				- kwargs (dict, optional): Keyword arguments for the callback
			repeat_delay (float, optional): Time in seconds before key repeat begins. Defaults to 0.5.
			repeat_interval (float, optional): Time in seconds between repeated triggers. Defaults to 0.1.
		"""
		self.hotkey_actions = hotkey_actions
		self.repeat_delay = repeat_delay
		self.repeat_interval = repeat_interval
		self.key_states = {}
		self.setup_listeners()

	def setup_listeners(self):
		"""Set up keyboard listeners for all defined hotkeys"""
		for key in self.hotkey_actions.keys():
			keyboard.on_press_key(key, self.on_key_press, suppress=True)
			keyboard.on_release_key(key, self.on_key_release)

	def get_pressed_modifiers(self):
		"""Get currently pressed modifier keys"""
		modifiers = []
		for mod in ["ctrl", "alt", "shift"]:
			if keyboard.is_pressed(mod):
				modifiers.append(mod)
		return tuple(sorted(modifiers))

	def find_matching_action(self, key, current_modifiers):
		"""Find the action that matches the current modifier combination"""
		if key not in self.hotkey_actions:
			return None

		for action in self.hotkey_actions[key]:
			if action["modifiers"] == current_modifiers:
				return action
		return None

	def on_key_press(self, event):
		"""Handle key press events with support for multiple modifier combinations"""
		key = event.name
		current_time = time.time()
		current_modifiers = self.get_pressed_modifiers()

		# Find matching action for current modifier combination
		action = self.find_matching_action(key, current_modifiers)
		if not action:
			print(f"no action: {action}")
			print(key)
			keyboard.press(key)
			return

		# Initialize or update key state
		state_key = (key, current_modifiers)
		if state_key not in self.key_states:
			self.key_states[state_key] = {
				"pressed": False,
				"last_trigger": 0,
				"repeat_started": False
			}

		# Handle initial press and repeats
		if not self.key_states[state_key]["pressed"]:
			self.trigger_action(action)
			self.key_states[state_key]["pressed"] = True
			self.key_states[state_key]["last_trigger"] = current_time
			self.key_states[state_key]["repeat_started"] = False
		else:
			time_held = current_time - self.key_states[state_key]["last_trigger"]

			if not self.key_states[state_key]["repeat_started"]:
				if time_held >= self.repeat_delay:
					self.key_states[state_key]["repeat_started"] = True
					self.trigger_action(action)
					self.key_states[state_key]["last_trigger"] = current_time
			else:
				if time_held >= self.repeat_interval:
					self.trigger_action(action)
					self.key_states[state_key]["last_trigger"] = current_time

	def on_key_release(self, event):
		"""Reset key state on release"""
		key = event.name
		current_modifiers = self.get_pressed_modifiers()
		state_key = (key, current_modifiers)

		if state_key in self.key_states:
			self.key_states[state_key]["pressed"] = False
			self.key_states[state_key]["repeat_started"] = False

	def trigger_action(self, action):
		"""Execute the callback function with its arguments"""
		callback = action["callback"]
		args = action.get("args", ())
		kwargs = action.get("kwargs", {})
		callback(*args, **kwargs)

	def stop(self):
		"""Clean up keyboard listeners"""
		keyboard.unhook_all()
