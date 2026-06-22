from PyQt5 import QtWidgets
from .common import fill_table
from desktop.api_client import APIError


class DevicesPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__(); self.client = client
        root = QtWidgets.QVBoxLayout(self)
        buttons = QtWidgets.QHBoxLayout()
        capture = QtWidgets.QPushButton("Capture Mock Camera Image"); capture.clicked.connect(self.capture)
        laser = QtWidgets.QPushButton("Read Mock Laser Profile"); laser.clicked.connect(self.laser)
        plc = QtWidgets.QPushButton("Read Mock PLC Tags"); plc.clicked.connect(self.plc)
        for widget in [capture, laser, plc]: buttons.addWidget(widget)
        root.addLayout(buttons)
        self.output = QtWidgets.QTextEdit(); self.output.setReadOnly(True); root.addWidget(self.output)

    def capture(self):
        try:
            payload = self.client.get("demo/camera/capture/")
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save synthetic capture", "mock_capture.png", "PNG (*.png)")
            if path:
                open(path, "wb").write(payload); self.output.setPlainText(f"Saved synthetic camera image to {path}")
        except APIError as exc: self.output.setPlainText(str(exc))

    def laser(self):
        try:
            data = self.client.get("demo/laser/profile/?points=32"); self.output.setPlainText(str(data))
        except APIError as exc: self.output.setPlainText(str(exc))

    def plc(self):
        try: self.output.setPlainText(str(self.client.get("demo/plc/")))
        except APIError as exc: self.output.setPlainText(str(exc))
