import PySide6.QtGui, os
# from PIL import Image
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QImage, QPixmap
from PySide6.QtWidgets import *
from Model.GlobalViewModel import GlobalViewModel
from Model.ImageLabelModel import ImageLabelModel


class LabelImage(QLabel):
    __global_vm: GlobalViewModel
    __labelimg_vm: ImageLabelModel
    # 灰度版本
    grayImage: None

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ''''''
        self.setStyleSheet("border:3px solid #242424;")

    def setPixmap(self, filename: str):
        '''
        设置显示的图片
        :param filename:文件的地址
        '''
        img = QImage()
        if not img.load(filename):
            QMessageBox.warning(self, "warn", "file not found")
            return
        self.__labelimg_vm.setImage(img)
        self.__labelimg_vm.computeOrigin(self.width(), self.height())
        pimg = QPixmap.fromImage(img)
        super().setPixmap(pimg)
        self.__global_vm.lastOpenDir = os.path.dirname(filename)

    def initialize(self, gloablvm: GlobalViewModel):
        self.__global_vm = gloablvm
        self.__labelimg_vm = gloablvm.imgModel
        print(self.__labelimg_vm)
        self.__labelimg_vm.resetImage.connect(self.reset)

    def reset(self, img):
        super().setPixmap(QPixmap.fromImage(img))

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.pixmap().isNull():
            return
        self.__labelimg_vm.computeOrigin(self.width(), self.height())

    def mousePressEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mousePressEvent(ev)
        color: int = Qt.red
        if ev.button() is Qt.MouseButton.RightButton:
            color = Qt.blue
        elif ev.button() is Qt.MouseButton.LeftButton:
            color = Qt.red
        self.__labelimg_vm.start(ev.pos().x(), ev.pos().y(), color)

    def paintEvent(self, arg__1: PySide6.QtGui.QPaintEvent) -> None:
        super().paintEvent(arg__1)
        painter = QPainter(self)
        self.__labelimg_vm.draw(painter)
        painter.end()
        self.update()

    def mouseMoveEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(ev)
        self.__labelimg_vm.update(ev.pos().x(), ev.pos().y())
        self.update()

    def mouseReleaseEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(ev)
        self.__labelimg_vm.end(ev.pos().x(), ev.pos().y())
        self.update()


if __name__ == "__main__":
    from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QApplication
    from UI.Component.LabelImage import LabelImage
    from Model.GlobalViewModel import GlobalViewModel
    from PySide6.QtGui import *
    import os, sys


    class TestLabelImage(QMainWindow):

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            m = GlobalViewModel()
            self.center = QWidget(self)
            self.center.setStyleSheet("border:3px solid #242424;")
            hlayout = QHBoxLayout(self.center)

            self.img = LabelImage(self.center)
            hlayout.addWidget(self.img)
            self.img.initialize(m)
            self.img.setPixmap("/data/home/yeep/Desktop/graduate/qt/app/MIDeepSeg/Res/Image/logo.png")
            self.setCentralWidget(self.center)
            self.setMinimumSize(800, 800)
            self.show()


    app = QApplication()
    main = TestLabelImage()
    sys.exit(app.exec())
