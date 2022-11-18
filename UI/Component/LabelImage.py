import PySide6.QtGui, os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QImage, QPixmap
from PySide6.QtWidgets import *
from Model.GlobalViewModel import GlobalViewModel
from Model.ImageLabelModel import ImageLabelModel


class LabelImage(QLabel):
    __global_vm: GlobalViewModel
    __labelimg_vm: ImageLabelModel

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
        self.__labelimg_vm = gloablvm.img_vm



    # def mouseReleaseEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
    #     super().mouseReleaseEvent(ev)
    #     self.__labelimg_vm.seed_type = SEED_TYPE.No

    # def mousePressEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
    #     super().mousePressEvent(ev)
    #     if ev.button() is Qt.MouseButton.RightButton:
    #         self.__labelimg_vm.seed_type = SEED_TYPE.NEGATIVE
    #     elif ev.button() is Qt.MouseButton.LeftButton:
    #         self.__labelimg_vm.seed_type = SEED_TYPE.POSITIVE

    # def mouseMoveEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
    #     super().mouseMoveEvent(ev)
    #     if self.__labelimg_vm.seed_type == SEED_TYPE.NEGATIVE:
    #         self.__labelimg_vm.addNativeSeed(ev.pos().x(), ev.pos().y())
    #     elif self.__labelimg_vm.seed_type == SEED_TYPE.POSITIVE:
    #         self.__labelimg_vm.addPositiveSeed(ev.pos().x(), ev.pos().y())

    # def paintEvent(self, arg__1: PySide6.QtGui.QPaintEvent) -> None:
    #
    #     super().paintEvent(arg__1)
    #     painter = QPainter(self)
    #     painter.setPen(QPen(Qt.blue, 6))
    #     for (x, y) in self.__labelimg_vm.backgroundSeed:
    #         xr, yr = self.__labelimg_vm.recoverToAbs(x, y)
    #         p = QPoint(xr, yr)
    #         painter.drawPoint(p)
    #
    #     painter.setPen(QPen(Qt.red, 6))
    #     for (x, y) in self.__labelimg_vm.foregoundSeed:
    #         xr, yr = self.__labelimg_vm.recoverToAbs(x, y)
    #         p = QPoint(xr, yr)
    #         painter.drawPoint(p)
    #     painter.end()
    #     self.update()

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
