import sys
from PySide6.QtWidgets import QApplication, QStyleFactory

from UI.ApplicationWindow import ApplicationWindow

if __name__ == "__main__":
    app = QApplication()
    main = ApplicationWindow()
    main.setStyle(QStyleFactory.create("window"))
    sys.exit(app.exec())
