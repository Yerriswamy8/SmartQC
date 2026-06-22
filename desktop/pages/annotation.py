from PyQt5 import QtCore, QtGui, QtWidgets
from desktop.api_client import APIError


class AnnotationCanvas(QtWidgets.QLabel):
    rectangle_created = QtCore.pyqtSignal(tuple)

    def __init__(self):
        super().__init__("Load an inspection image")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumHeight(500)
        self.setStyleSheet("border:1px solid #475569; background:#020617;")
        self.original = None; self.displayed = None; self.start = None; self.end = None

    def load_image(self, path):
        self.original = QtGui.QPixmap(path)
        self._update_display()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_display()

    def _update_display(self):
        if self.original:
            self.displayed = self.original.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.setPixmap(self.displayed)

    def mousePressEvent(self, event):
        if self.original and event.button() == QtCore.Qt.LeftButton:
            self.start = event.pos(); self.end = event.pos(); self.update()

    def mouseMoveEvent(self, event):
        if self.start:
            self.end = event.pos(); self.update()

    def mouseReleaseEvent(self, event):
        if not self.start or not self.displayed: return
        self.end = event.pos()
        offset_x = (self.width() - self.displayed.width()) / 2
        offset_y = (self.height() - self.displayed.height()) / 2
        scale_x = self.original.width() / self.displayed.width()
        scale_y = self.original.height() / self.displayed.height()
        x1 = max(0, min(self.start.x(), self.end.x()) - offset_x) * scale_x
        y1 = max(0, min(self.start.y(), self.end.y()) - offset_y) * scale_y
        x2 = max(0, max(self.start.x(), self.end.x()) - offset_x) * scale_x
        y2 = max(0, max(self.start.y(), self.end.y()) - offset_y) * scale_y
        self.rectangle_created.emit((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
        self.start = self.end = None; self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start and self.end:
            painter = QtGui.QPainter(self); painter.setPen(QtGui.QPen(QtGui.QColor(0, 220, 255), 2)); painter.drawRect(QtCore.QRect(self.start, self.end).normalized())


class AnnotationPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__(); self.client = client; self.image_id = None; self.coords = None
        root = QtWidgets.QVBoxLayout(self)
        controls = QtWidgets.QHBoxLayout()
        self.image_id_input = QtWidgets.QSpinBox(); self.image_id_input.setMaximum(999999); self.image_id_input.setPrefix("Image ID: ")
        self.label = QtWidgets.QLineEdit("manual_defect"); self.author = QtWidgets.QLineEdit("Demo Annotator")
        load = QtWidgets.QPushButton("Load Local Image"); load.clicked.connect(self.load_image)
        save = QtWidgets.QPushButton("Save Rectangle to API"); save.clicked.connect(self.save_annotation)
        for widget in [self.image_id_input, self.label, self.author, load, save]: controls.addWidget(widget)
        root.addLayout(controls)
        self.canvas = AnnotationCanvas(); self.canvas.rectangle_created.connect(self.on_rectangle); root.addWidget(self.canvas)
        self.status = QtWidgets.QLabel("Draw one rectangle with the mouse."); root.addWidget(self.status)

    def load_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path: self.canvas.load_image(path)

    def on_rectangle(self, coords):
        self.coords = coords; self.status.setText(f"Rectangle: {coords}")

    def save_annotation(self):
        if not self.coords:
            QtWidgets.QMessageBox.warning(self, "Rectangle required", "Draw a rectangle first."); return
        x1, y1, x2, y2 = self.coords
        try:
            response = self.client.post("annotations/", json={"image": self.image_id_input.value(), "label": self.label.text().strip(), "created_by": self.author.text().strip(), "x1": x1, "y1": y1, "x2": x2, "y2": y2})
            self.status.setText(f"Saved annotation ID {response['id']}")
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Save failed", str(exc))
