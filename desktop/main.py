import os
import sys
from PyQt5 import QtWidgets
from desktop.api_client import SmartQCClient
from desktop.theme import APP_STYLE
from desktop.pages.dashboard import DashboardPage
from desktop.pages.machines import MachinesPage
from desktop.pages.projects import ProjectsPage
from desktop.pages.inspection import InspectionPage
from desktop.pages.annotation import AnnotationPage
from desktop.pages.devices import DevicesPage
from desktop.pages.operator import OperatorPage


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartQC Demo - Industrial Inspection Platform")
        self.resize(1450, 900)
        client = SmartQCClient(os.getenv("SMARTQC_API_URL", "http://127.0.0.1:8000/api"))
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(DashboardPage(client), "Dashboard")
        tabs.addTab(MachinesPage(client), "Machines")
        tabs.addTab(ProjectsPage(client), "Projects")
        tabs.addTab(InspectionPage(client), "Inspection")
        tabs.addTab(AnnotationPage(client), "Annotation")
        tabs.addTab(DevicesPage(client), "Mock Devices")
        tabs.addTab(OperatorPage(client), "Operators")
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Demo mode: no production PLC, camera, laser, model, or customer data is used.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = MainWindow(); window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
