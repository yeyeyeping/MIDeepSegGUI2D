from typing import Optional

import PySide6.QtCore
import PySide6.QtGui
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import *
from PySide6.QtGui import QPainter, QPen, QImage, QPixmap
from Model.GlobalViewModel import GlobalViewModel
from Model.ImageLabelModel import ImageLabelModel, SEED_TYPE


class LabelImage(QLabel):
    __global_vm: GlobalViewModel
    __labelimg_vm: ImageLabelModel

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

    def mouseReleaseEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(ev)
        self.__labelimg_vm.seed_type = SEED_TYPE.No

    def initialize(self, gloablvm: GlobalViewModel):
        self.__global_vm = gloablvm
        self.__labelimg_vm = gloablvm.img_vm

    def mousePressEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mousePressEvent(ev)
        if ev.button() is Qt.MouseButton.RightButton:
            self.__labelimg_vm.seed_type = SEED_TYPE.NEGATIVE
        elif ev.button() is Qt.MouseButton.LeftButton:
            self.__labelimg_vm.seed_type = SEED_TYPE.POSITIVE

    def mouseMoveEvent(self, ev: PySide6.QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(ev)
        if self.__labelimg_vm.seed_type == SEED_TYPE.NEGATIVE:
            self.__labelimg_vm.addNativeSeed(ev.pos().x(), ev.pos().y())
        elif self.__labelimg_vm.seed_type == SEED_TYPE.POSITIVE:
            self.__labelimg_vm.addPositiveSeed(ev.pos().x(), ev.pos().y())

    def paintEvent(self, arg__1: PySide6.QtGui.QPaintEvent) -> None:

        super().paintEvent(arg__1)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.blue, 6))
        for (x, y) in self.__labelimg_vm.backgroundSeed:
            xr, yr = self.__labelimg_vm.recoverToAbs(x, y)
            p = QPoint(xr, yr)
            painter.drawPoint(p)

        painter.setPen(QPen(Qt.red, 6))
        for (x, y) in self.__labelimg_vm.foregoundSeed:
            xr, yr = self.__labelimg_vm.recoverToAbs(x, y)
            p = QPoint(xr, yr)
            painter.drawPoint(p)
        painter.end()
        self.update()

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.__labelimg_vm.computeOrigin(self.width(), self.height())
