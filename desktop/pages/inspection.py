from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from desktop.api_client import APIError
from .common import fill_table


class InspectionPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.image_path = None
        root = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QHBoxLayout()
        self.machine = QtWidgets.QComboBox(); self.project = QtWidgets.QComboBox()
        self.serial = QtWidgets.QLineEdit(); self.serial.setPlaceholderText("Part/tyre serial number")
        self.operator = QtWidgets.QLineEdit(); self.operator.setPlaceholderText("Operator")
        select = QtWidgets.QPushButton("Select Image"); select.clicked.connect(self.select_image)
        run = QtWidgets.QPushButton("Create + Inspect"); run.clicked.connect(self.run_inspection)
        for widget in [self.machine, self.project, self.serial, self.operator, select, run]: form.addWidget(widget)
        root.addLayout(form)
        self.preview = QtWidgets.QLabel("Select an image or use sample_data/inspection_sample.png")
        self.preview.setAlignment(QtCore.Qt.AlignCenter); self.preview.setMinimumHeight(430)
        self.preview.setStyleSheet("border:1px solid #475569; background:#020617;")
        root.addWidget(self.preview)
        self.result = QtWidgets.QLabel("Decision: -"); root.addWidget(self.result)
        self.table = QtWidgets.QTableWidget(); root.addWidget(self.table)
        refresh = QtWidgets.QPushButton("Reload Machine and Project Lists"); refresh.clicked.connect(self.load_reference_data); root.addWidget(refresh)
        self.load_reference_data()

    def load_reference_data(self):
        try:
            machines = self.client.list_machines(); projects = self.client.list_projects()
            self.machine.clear(); self.project.clear()
            for row in machines: self.machine.addItem(f"{row['code']} - {row['name']}", row['id'])
            for row in projects: self.project.addItem(f"{row['code']} - {row['name']}", row['id'])
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))

    def select_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose inspection image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.image_path = path
            pixmap = QtGui.QPixmap(path)
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def run_inspection(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "Image required", "Select an image first."); return
        if self.machine.currentData() is None or self.project.currentData() is None:
            QtWidgets.QMessageBox.warning(self, "Setup required", "Create demo data or add a machine and project."); return
        serial = self.serial.text().strip() or f"DEMO-{QtCore.QDateTime.currentDateTime().toString('yyyyMMddHHmmss')}"
        try:
            inspection = self.client.create_inspection({
                "machine": self.machine.currentData(), "project": self.project.currentData(),
                "serial_number": serial, "operator_name": self.operator.text().strip(),
                "status": "RUNNING", "decision": "UNKNOWN", "metadata": {"source": "desktop"},
            })
            result = self.client.upload_and_inspect(inspection["id"], self.image_path)
            detections = result.get("images", [{}])[0].get("detections", []) if result.get("images") else []
            self.result.setText(f"Decision: {result['decision']} | Defects: {result['defect_count']} | Cycle: {result['cycle_time_ms']} ms")
            self.result.setObjectName("StatusDefect" if result["decision"] == "DEFECT" else "StatusGood")
            self.result.style().unpolish(self.result); self.result.style().polish(self.result)
            fill_table(self.table, detections, [("label", "Label"), ("confidence", "Confidence"), ("x1", "X1"), ("y1", "Y1"), ("x2", "X2"), ("y2", "Y2"), ("area_px", "Area")])
            self.draw_detections(detections)
        except APIError as exc:
            QtWidgets.QMessageBox.critical(self, "Inspection failed", str(exc))

    def draw_detections(self, detections):
        pixmap = QtGui.QPixmap(self.image_path)
        painter = QtGui.QPainter(pixmap); pen = QtGui.QPen(QtGui.QColor(255, 40, 40), 4); painter.setPen(pen)
        font = painter.font(); font.setPointSize(12); font.setBold(True); painter.setFont(font)
        for item in detections:
            rect = QtCore.QRectF(float(item["x1"]), float(item["y1"]), float(item["x2"])-float(item["x1"]), float(item["y2"])-float(item["y1"]))
            painter.drawRect(rect); painter.drawText(rect.topLeft() + QtCore.QPointF(0, -5), f"{item['label']} {float(item['confidence']):.2f}")
        painter.end()
        self.preview.setPixmap(pixmap.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
