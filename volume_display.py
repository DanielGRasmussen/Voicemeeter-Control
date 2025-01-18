import logging
from threading import Lock

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

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


class VolumeDisplay(QWidget):
	"""
	A floating volume notification widget that appears briefly when volume changes occur.
	
	Features:
	- Frameless, always-on-top window
	- Semi-transparent background
	- Auto-hiding after a short delay
	- Thread-safe notification display
	- Dynamic sizing based on content
	- Positioned in the bottom-right corner
	- Right-aligned text with consistent styling
	- Non-intrusive (doesn't steal focus)
	"""

	def __init__(self):
		"""
		Initialize the volume display widget.
		Sets up the UI components and configures window behavior.
		"""
		super().__init__()
		self.hide_timer = None
		self.init_ui()
		self.timer_lock = Lock()

	def init_ui(self):
		"""
		Set up the user interface components and styling.
		Configures window flags, layout, label, and timer for auto-hiding.
		"""
		# Set up the window
		self.setWindowFlags(
			Qt.FramelessWindowHint |
			Qt.WindowStaysOnTopHint |
			Qt.Tool
		)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setAttribute(Qt.WA_ShowWithoutActivating)

		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(0, 0, 0, 0)

		# Create label for text
		self.label = QLabel()
		self.label.setStyleSheet("""
			QLabel {
				color: white;
				background-color: rgba(64, 64, 64, 200);
				padding: 4px 8px;
				border-radius: 10px;
				font-family: Segoe UI, Arial;
				font-size: 16px;
			}
		""")
		self.layout.addWidget(self.label)

		self.hide_timer = QTimer(self)
		self.hide_timer.timeout.connect(self.hide)
		self.hide_timer.setSingleShot(True)

		# Initialize with minimum size
		self.update_size("")

	def update_size(self, text):
		"""
		Calculate and set the widget size based on the text content.
		
		Args:
			text (str): The text to be displayed in the notification
		"""
		# Calculate required width based on text
		metrics = QFontMetrics(self.label.font())
		text_width = metrics.horizontalAdvance(text)

		width = text_width + 20 # Padding + Something seems to be off
		height = 40

		# Update sizes
		self.label.setFixedSize(width, height)
		self.setFixedSize(width, height)

	def show_notification(self, text):
		"""
		Display a notification with the specified text.
		The notification appears in the bottom-right corner and auto-hides after 1.5 seconds.
		
		Args:
			text (str): The text to display in the notification
			
		Thread Safety:
			Uses a lock to ensure thread-safe timer manipulation
			
		Notes:
			- Positions itself 20px from the right and 80px from the bottom of the screen
			- Right-aligns the text within the notification
			- Automatically resizes based on text content
		"""
		try:
			# Update text (right-aligned)
			self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
			self.label.setText(text)

			self.update_size(text)

			# Position window in bottom right
			screen = QApplication.primaryScreen().geometry()
			self.move(
				screen.width() - self.width() - 20,
				screen.height() - self.height() - 80
			)

			self.show()

			# Reset and start timer
			with self.timer_lock:
				self.hide_timer.stop()
				self.hide_timer.start(1500)

		except Exception as e:
			logger.error(f"Error showing notification: {str(e)}")
