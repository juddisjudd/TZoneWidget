import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QFont
import logging
import json

with open('zone_mappings.json', 'r') as f:
    ZONE_MAPPINGS = json.load(f)

logging.basicConfig(filename='application.log', level=logging.INFO)

class ZoneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.current_zone_name = "Initializing..."
        self.next_zone_name = "Initializing..."

        self.start_update_loop()
        self.old_pos = self.pos()

    def initUI(self):
        """Initialize the UI components and set up the layout."""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 160);")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.current_zone_label = self.create_label("#4cd137", "Current Zone: Initializing...")
        self.next_zone_label = self.create_label("#fbc531", "Next Zone: Initializing...")

        close_button_style = """
        QPushButton {
            background-color: rgba(0, 0, 0, 160);
            color: white;
            padding: 6px 6px;
            font-size: 12px;
            border-radius: 4px;
            min-width: 14px;
            min-height: 14px;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 160);
            color: red;
        }
        QPushButton:pressed {
            background-color: rgba(0, 0, 0, 160);
        }
        """
        self.close_button = QPushButton("X")
        self.close_button.setStyleSheet(close_button_style)
        self.close_button.setFixedSize(14, 14)
        self.close_button.clicked.connect(self.close)

        layout.addWidget(self.current_zone_label)
        layout.addWidget(self.next_zone_label)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(475, 125)

        font = QFont()
        font.setFamily("Arial")
        font.setBold(True)
        self.setFont(font)

    def create_label(self, color, text):
        """Create a label with the specified color and text."""
        label_style = f"QLabel {{ background-color: rgba(0, 0, 0, 120); color: {color}; padding: 2px; font-size: 14px; border-radius: 4px; text-transform: uppercase;}}"
        label = QLabel(text)
        label.setStyleSheet(label_style)
        return label

    def mousePressEvent(self, event):
        """Handle mouse press events to enable window dragging."""
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """Handle mouse move events to update the window position."""
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def start_update_loop(self):
        """Start the update loop for fetching terror zone data."""
        self.update_info()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(10000)  # Update every 10 seconds

    def update_info(self):
        """Fetch terror zone data and update the UI."""
        try:
            self.fetch_terror_zone_data()
        except Exception as e:
            logging.error(f"Error fetching terror zone data: {e}")

    def fetch_terror_zone_data(self):
        """Fetch terror zone data from the API and update the UI."""
        url = 'https://www.d2emu.com/api/v1/tz'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current_zone_data = self.get_zone_data_from_ids(data['current'])
        next_zone_data = self.get_zone_data_from_ids(data['next'])

        self.current_zone_name = current_zone_data.get("location", "Unknown")
        self.next_zone_name = next_zone_data.get("location", "Unknown")

        self.update_ui()

    def get_zone_data_from_ids(self, ids_list):
        """Get the zone data from a list of zone IDs."""
        zone_data = {str(zone_id): ZONE_MAPPINGS.get(str(zone_id), {"location": f"Zone {zone_id}"}) for zone_id in ids_list}
        return next(iter(zone_data.values()))

    def update_ui(self):
        """Update the UI with the current and next zone names."""
        self.current_zone_label.setText(f"Current Zone: {self.current_zone_name}")
        self.next_zone_label.setText(f"Next Zone: {self.next_zone_name}")

    def customEvent(self, event):
        """Handle custom events for updating the UI."""
        self.update_ui()

class CustomEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, current_zone, next_zone):
        super().__init__(CustomEvent.EVENT_TYPE)
        self.current_zone = current_zone
        self.next_zone = next_zone

if __name__ == "__main__":
    app = QApplication(sys.argv)
    zone_widget = ZoneWidget()
    zone_widget.show()
    sys.exit(app.exec_())
