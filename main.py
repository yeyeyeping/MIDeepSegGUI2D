import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from qt_material import apply_stylesheet
from UI.ApplicationWindow import ApplicationWindow

if __name__ == "__main__":
    app = QApplication()
    main = ApplicationWindow()
    apply_stylesheet(main, theme='light_cyan.xml')
    sys.exit(app.exec())
