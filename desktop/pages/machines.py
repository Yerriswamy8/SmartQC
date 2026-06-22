from PyQt5 import QtWidgets
from .common import fill_table
from desktop.api_client import APIError


class MachinesPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        root = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QHBoxLayout()
        self.code = QtWidgets.QLineEdit(); self.code.setPlaceholderText("Code, e.g. DEMO-LINE-02")
        self.name = QtWidgets.QLineEdit(); self.name.setPlaceholderText("Machine name")
        self.location = QtWidgets.QLineEdit(); self.location.setPlaceholderText("Location")
        add = QtWidgets.QPushButton("Add Machine"); add.clicked.connect(self.add_machine)
        for widget in [self.code, self.name, self.location, add]: form.addWidget(widget)
        root.addLayout(form)
        self.table = QtWidgets.QTableWidget(); self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        root.addWidget(self.table)
        actions = QtWidgets.QHBoxLayout()
        for text, state in [("Start", "start"), ("Stop", "stop"), ("Simulate Error", "simulate-error")]:
            button = QtWidgets.QPushButton(text); button.clicked.connect(lambda _, s=state: self.set_state(s)); actions.addWidget(button)
        refresh = QtWidgets.QPushButton("Refresh"); refresh.clicked.connect(self.refresh); actions.addWidget(refresh)
        root.addLayout(actions)
        self.refresh()

    def refresh(self):
        try:
            self.rows = self.client.list_machines()
            fill_table(self.table, self.rows, [("id", "ID"), ("code", "Code"), ("name", "Name"), ("location", "Location"), ("status", "Status"), ("camera_count", "Cameras"), ("laser_count", "Lasers")])
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))

    def add_machine(self):
        try:
            self.client.create_machine({"code": self.code.text().strip(), "name": self.name.text().strip(), "location": self.location.text().strip(), "status": "IDLE", "plc_mode": "MOCK", "is_active": True, "configuration": {}})
            self.refresh()
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))

    def set_state(self, action):
        row = self.table.currentRow()
        if row < 0: return
        machine_id = self.table.item(row, 0).text()
        try:
            self.client.post(f"machines/{machine_id}/{action}/")
            self.refresh()
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))
