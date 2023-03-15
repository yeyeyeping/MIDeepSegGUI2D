from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtGui import QMouseEvent
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个 QLabel 控件，并将其设置为中央窗口部件
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.setMouseTracking(True)
        # 开启鼠标跟踪
        self.label.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # 获取鼠标的位置，并将其显示在 QLabel 控件中
        pos = event.pos()
        self.label.setText(f"Mouse position: ({pos.x()}, {pos.y()})")

# 创建应用程序对象和主窗口对象
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 启动应用程序的主事件循环
sys.exit(app.exec())
