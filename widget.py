import sys
import requests
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QFont

class ZoneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.zone_mapping = self.load_zone_mappings()
        self.current_zone_name_global = "Initializing..."
        self.next_zone_name_global = "Initializing..."

        self.start_update_loop()
        self.oldPos = self.pos()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 160);")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        labelStyle = "QLabel { background-color: rgba(0, 0, 0, 120); color: %s; padding: 2px; font-size: 14px; border-radius: 4px; text-transform: uppercase;}"
        greenLabelStyle = labelStyle % "#4cd137"
        yellowLabelStyle = labelStyle % "#fbc531"

        self.current_zone_label = QLabel("Current Zone: Initializing...")
        self.current_zone_label.setStyleSheet(greenLabelStyle)

        self.next_zone_label = QLabel("Next Zone: Initializing...")
        self.next_zone_label.setStyleSheet(yellowLabelStyle)

        closeButtonStyle = """
        QPushButton {
            background-color: rgba(0, 0, 0, 160);  /* Transparent background */
            color: white;
            padding: 6px 6px;
            font-size: 12px;
            border-radius: 4px;
            min-width: 14px;
            min-height: 14px;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 160);  /* Slightly visible on hover */
            color: red;
        }
        QPushButton:pressed {
            background-color: rgba(0, 0, 0, 160);  /* More visible when pressed */
        }
        """
        self.close_button = QPushButton("X")
        self.close_button.setStyleSheet(closeButtonStyle)
        self.close_button.setFixedSize(14, 14)
        self.close_button.clicked.connect(self.close)

        closeLayout = QHBoxLayout()
        closeLayout.addStretch(1)
        closeLayout.addWidget(self.close_button)
        closeLayout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.current_zone_label)
        layout.addWidget(self.next_zone_label)
        layout.addLayout(closeLayout)

        self.setLayout(layout)
        self.setFixedSize(475, 125)

        font = QFont()
        font.setFamily("Arial")
        font.setBold(True)
        self.setFont(font)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def load_zone_mappings(self):
        zone_data = {
          "2": {
              "location": "Blood Moor/Den of Evil"
          },
          "3": {
              "location": "Cold Plains/Cave"
          },
          "17": {
              "location": "Burial Grounds/Crypt/Mausoleum"
          },
          "4": {
              "location": "Stony Field"
          },
          "38": {
              "location": "Tristram"
          },
          "5": {
              "location": "Darkwood/Underground Passage"
          },
          "6": {
              "location": "Black Marsh/The Hole"
          },
          "20": {
              "location": "Forgotten Tower"
          },
          "12": {
              "location": "The Pit"
          },
          "28": {
              "location": "Jail/Barracks"
          },
          "33": {
              "location": "Cathedral/Catacombs"
          },
          "39": {
              "location": "The Secret Cow Level"
          },
          "47": {
              "location": "Lut Gholein Sewers"
          },
          "41": {
              "location": "Stony Tomb/Rocky Waste"
          },
          "42": {
              "location": "Dry Hills/Halls of the Dead"
          },
          "43": {
              "location": "Far Oasis"
          },
          "65": {
              "location": "Ancient Tunnels"
          },
          "44": {
              "location": "Lost City/Valley of Snakes/Claw Viper Temple"
          },
          "74": {
              "location": "Arcane Sanctuary"
          },
          "66": {
              "location": "Tal Rasha's Tombs"
          },
          "76": {
              "location": "Spider Forest/Spider Cavern"
          },
          "78": {
              "location": "Flayer Jungle and Dungeon"
          },
          "77": {
              "location": "Great Marsh"
          },
          "80": {
              "location": "Kurast Bazaar/Temples"
          },
          "83": {
              "location": "Travincal"
          },
          "100": {
              "location": "Durance of Hate"
          },
          "104": {
              "location": "Outer Steppes/Plains of Despair"
          },
          "106": {
              "location": "City of the Damned/River of Flame"
          },
          "108": {
              "location": "Chaos Sanctuary"
          },
          "110": {
              "location": "Bloody Foothills/Frigid Highlands/Abbadon"
          },
          "115": {
              "location": "Glacial Trail/Drifter Cavern"
          },
          "118": {
              "location": "Ancient's Way/Icy Cellar"
          },
          "112": {
              "location": "Arreat Plateau/Pit of Acheron"
          },
          "113": {
              "location": "Crystalline Passage/Frozen River"
          },
          "121": {
              "location": "Nihlathak's Temple and Halls"
          },
          "128": {
              "location": "Worldstone Keep/Throne of Destruction/Worldstone Chamber"
          }
        }
        return zone_data

    def start_update_loop(self):
        self.update_info()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(60000)

    def update_info(self):
        threading.Thread(target=self.fetch_terror_zone_data).start()

    def fetch_terror_zone_data(self):
        url = 'https://www.d2emu.com/api/v1/tz'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            current_zone_data = self.get_zone_data_from_ids(data['current'])
            next_zone_data = self.get_zone_data_from_ids(data['next'])

            self.current_zone_name_global = current_zone_data.get("location", "Unknown")
            self.next_zone_name_global = next_zone_data.get("location", "Unknown")

            QApplication.instance().postEvent(self, CustomEvent(self.current_zone_name_global, self.next_zone_name_global))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching terror zone data: {e}")

    def get_zone_data_from_ids(self, ids_list):
        for zone_id in ids_list:
            zone_data = self.zone_mapping.get(str(zone_id))
            if zone_data:
                return zone_data
        return {"location": f"Zone {ids_list[0]}"}

    def customEvent(self, event):
        self.current_zone_label.setText(f"Current Zone: {event.current_zone}")
        self.next_zone_label.setText(f"Next Zone: {event.next_zone}")

class CustomEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, current_zone, next_zone):
        super().__init__(CustomEvent.EVENT_TYPE)
        self.current_zone = current_zone
        self.next_zone = next_zone

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ZoneWidget()
    ex.show()
    sys.exit(app.exec_())
