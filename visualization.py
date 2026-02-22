import sys
import serial
import threading
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100, color='green', title=""):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_title(title)
        self.data = [0] * 30
        self.line, = self.axes.plot(self.data, color=color)
        self.axes.grid(True, alpha=0.3)
        super(MplCanvas, self).__init__(fig)

    def update_data(self, new_val):
        self.data.append(new_val)
        self.data.pop(0)
        self.line.set_ydata(self.data)
        self.axes.set_ylim(min(self.data) - 5, max(self.data) + 5)
        self.draw()

class SteeringWheelUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.active_sensors = [] # Indices 0-11

    def set_sensors(self, indices):
        self.active_sensors = indices
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = self.rect().center()
        radius = 130

        # Draw main wheel body
        painter.setPen(QPen(QColor(40, 44, 52), 35))
        painter.drawEllipse(center, radius, radius)

        # Draw sensors (30 degree increments as per your angle = i * 30)
        for i in range(12):
            angle_rad = np.radians(i * 30 - 90) # -90 to start from top
            x = center.x() + radius * np.cos(angle_rad)
            y = center.y() + radius * np.sin(angle_rad)

            color = QColor(142, 68, 173) if i in self.active_sensors else QColor(231, 76, 60)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - 10), int(y - 10), 20, 20)

class SmartSteeringSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Steering Monitoring System")
        self.showMaximized()
        self.setStyleSheet("background-color: #ffffff;")

        # Serial setup (Change 'COM3' to your Arduino port)
        try:
            self.ser = serial.Serial('COM3', 9600, timeout=0.1)
        except:
            self.ser = None
            print("Serial Connection Failed!")

        self.initUI()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_serial)
        self.timer.start(50)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)

        # Labels
        self.pulse_label = QLabel("Heart Rate: -- BPM")
        self.temp_label = QLabel("Temp: -- °C")
        self.status_label = QLabel("SYSTEM READY")
        
        for lbl in [self.pulse_label, self.temp_label]:
            lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))

        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: #27ae60; color: white; padding: 20px; font-size: 24px; border-radius: 10px;")

        # Visuals
        self.steering = SteeringWheelUI()
        self.pulse_chart = MplCanvas(self, color='#27ae60', title="Heart Rate Change")
        self.temp_chart = MplCanvas(self, color='#e74c3c', title="Body Temp Change")

        # Layout Arrangement
        main_layout.addWidget(self.pulse_label, 0, 0, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.steering, 0, 1, 2, 1)
        main_layout.addWidget(self.temp_label, 0, 2, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.pulse_chart, 1, 0)
        main_layout.addWidget(self.temp_chart, 1, 2)
        main_layout.addWidget(self.status_label, 2, 0, 1, 3)

    def process_serial(self):
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Parse Pulse
                if "Kalp Nabız Değeri:" in line:
                    val = int(line.split(":")[-1].strip())
                    self.pulse_label.setText(f"Heart Rate: {val} BPM")
                    self.pulse_chart.update_data(val)

                # Parse Temperature
                elif "Ateş" in line:
                    temp_str = ''.join(c for c in line.split(":")[-1] if c.isdigit() or c == '.')
                    val = float(temp_str)
                    self.temp_label.setText(f"Temp: {val} °C")
                    self.temp_chart.update_data(val)

                # Parse Hand Positions
                elif "Ellerin Konumu:" in line:
                    # Extracts numeric angles and converts back to indices
                    parts = line.split(":")[-1].strip().split()
                    indices = []
                    for p in parts:
                        if p.isdigit():
                            indices.append(int(p) // 30)
                    self.steering.set_sensors(indices)
                
                # Update status based on keywords in your Arduino code
                if "Doğru el tutuşu" in line:
                    self.status_label.setText("SAFE DRIVING")
                    self.status_label.setStyleSheet("background-color: #27ae60; color: white; padding: 20px; font-size: 24px; border-radius: 10px;")
                elif "Yanlış el tutuşu" in line or "Eller algılanmadı" in line:
                    self.status_label.setText("WARNING: GRIP ERROR")
                    self.status_label.setStyleSheet("background-color: #e67e22; color: white; padding: 20px; font-size: 24px; border-radius: 10px;")
                elif "UYARI VER: Ateş" in line:
                    self.status_label.setText("CRITICAL: FEVER DETECTED")
                    self.status_label.setStyleSheet("background-color: #c0392b; color: white; padding: 20px; font-size: 24px; border-radius: 10px;")

            except Exception as e:
                print(f"Data Parsing Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartSteeringSystem()
    window.show()
    sys.exit(app.exec_())