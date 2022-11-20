import sys
from PySide6.QtWidgets import QApplication

from UI.ApplicationWindow import ApplicationWindow

if __name__ == "__main__":
    app = QApplication()
    main = ApplicationWindow()
    sys.exit(app.exec())
