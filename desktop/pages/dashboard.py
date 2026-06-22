from PyQt5 import QtWidgets
from .common import fill_table
from desktop.api_client import APIError


class DashboardPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        root = QtWidgets.QVBoxLayout(self)
        metrics = QtWidgets.QHBoxLayout()
        self.labels = {}
        for key, title in [("total_inspections", "Inspections"), ("good", "Good"), ("defect", "Defects"), ("machines_running", "Machines Running")]:
            box = QtWidgets.QGroupBox(title)
            layout = QtWidgets.QVBoxLayout(box)
            label = QtWidgets.QLabel("0")
            label.setObjectName("MetricValue")
            layout.addWidget(label)
            metrics.addWidget(box)
            self.labels[key] = label
        root.addLayout(metrics)
        self.table = QtWidgets.QTableWidget()
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table)
        button = QtWidgets.QPushButton("Refresh Dashboard")
        button.clicked.connect(self.refresh)
        root.addWidget(button)
        self.refresh()

    def refresh(self):
        try:
            data = self.client.get("dashboard/stats/")
            for key, label in self.labels.items():
                label.setText(str(data.get(key, 0)))
            fill_table(self.table, data.get("recent_inspections", []), [
                ("id", "ID"), ("serial_number", "Serial"), ("machine", "Machine"),
                ("project", "Project"), ("decision", "Decision"), ("defect_count", "Defects"),
            ])
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "API unavailable", str(exc))
