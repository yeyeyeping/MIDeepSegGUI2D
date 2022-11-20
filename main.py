import os
import sys

from PySide6.QtWidgets import QApplication

from Logic.Common.NetworkDelegate import NetworkDelegate
from UI.ApplicationWindow import ApplicationWindow
from Logic.utils.Pathdb import get_resource_path
if __name__ == "__main__":
    app = QApplication()
    main = ApplicationWindow()
    sys.exit(app.exec())

