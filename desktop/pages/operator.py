from PyQt5 import QtWidgets
from .common import fill_table
from desktop.api_client import APIError


class OperatorPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__(); self.client = client
        root = QtWidgets.QVBoxLayout(self); form = QtWidgets.QHBoxLayout()
        self.machine = QtWidgets.QComboBox(); self.name = QtWidgets.QLineEdit(); self.name.setPlaceholderText("Operator name")
        self.state = QtWidgets.QComboBox(); self.state.addItems(["ACTIVE", "BREAK", "OFFLINE"])
        self.message = QtWidgets.QLineEdit(); self.message.setPlaceholderText("Optional note")
        send = QtWidgets.QPushButton("Send Heartbeat"); send.clicked.connect(self.send)
        for widget in [self.machine, self.name, self.state, self.message, send]: form.addWidget(widget)
        root.addLayout(form); self.table = QtWidgets.QTableWidget(); root.addWidget(self.table)
        refresh = QtWidgets.QPushButton("Refresh"); refresh.clicked.connect(self.refresh); root.addWidget(refresh)
        self.load_machines(); self.refresh()

    def load_machines(self):
        try:
            self.machine.clear()
            for row in self.client.list_machines(): self.machine.addItem(row["code"], row["id"])
        except APIError: pass

    def send(self):
        try:
            self.client.post("operator-heartbeats/", json={"machine": self.machine.currentData(), "operator_name": self.name.text().strip(), "state": self.state.currentText(), "message": self.message.text().strip()}); self.refresh()
        except APIError as exc: QtWidgets.QMessageBox.warning(self, "Error", str(exc))

    def refresh(self):
        try:
            rows = self.client.rows(self.client.get("operator-heartbeats/?ordering=-last_seen"))
            fill_table(self.table, rows, [("id", "ID"), ("operator_name", "Operator"), ("machine_code", "Machine"), ("state", "State"), ("message", "Message"), ("last_seen", "Last Seen")])
        except APIError as exc: QtWidgets.QMessageBox.warning(self, "Error", str(exc))
