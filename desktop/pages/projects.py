from PyQt5 import QtWidgets
from .common import fill_table
from desktop.api_client import APIError


class ProjectsPage(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        root = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QHBoxLayout()
        self.code = QtWidgets.QLineEdit(); self.code.setPlaceholderText("Project code")
        self.name = QtWidgets.QLineEdit(); self.name.setPlaceholderText("Project name")
        self.description = QtWidgets.QLineEdit(); self.description.setPlaceholderText("Description")
        add = QtWidgets.QPushButton("Add Project"); add.clicked.connect(self.add_project)
        for widget in [self.code, self.name, self.description, add]: form.addWidget(widget)
        root.addLayout(form)
        self.table = QtWidgets.QTableWidget(); root.addWidget(self.table)
        refresh = QtWidgets.QPushButton("Refresh"); refresh.clicked.connect(self.refresh); root.addWidget(refresh)
        self.refresh()

    def refresh(self):
        try:
            self.rows = self.client.list_projects()
            fill_table(self.table, self.rows, [("id", "ID"), ("code", "Code"), ("name", "Name"), ("status", "Status"), ("recipe_count", "Recipes"), ("model_count", "Models")])
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))

    def add_project(self):
        try:
            self.client.create_project({"code": self.code.text().strip(), "name": self.name.text().strip(), "description": self.description.text().strip(), "status": "ACTIVE"})
            self.refresh()
        except APIError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", str(exc))
