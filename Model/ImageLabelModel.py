import cv2
import numpy as np
from PySide6.QtGui import QImage, QPainter, QPen, Qt, QPixmap
from PySide6.QtCore import QObject, QPoint
from PySide6.QtCore import Slot, Signal
from PySide6.QtWidgets import QMessageBox

from Logic.utils.utils import QImageToCvMat
from Model.Scribble import SCRIBBLE_TYPE
import Model
from Logic.utils.utils import QImageToGrayCvMat


class ImageLabelModel(QObject):
    resetImage = Signal(QImage)
    __m_parent = None
    # 图片左上角相对与Qlabel左上角的偏移
    __originX: int
    __originY: int
    # Qlabel内显示的图片的长度和宽度，用于计算左上角的坐标
    __imgW: int
    __imgH: int
    rawImage: QImage

    cur_scribble_type: SCRIBBLE_TYPE
    scribbles: list

    __initialseg_end: bool

    # 用户给的点击点对应的位置
    __extrem_pos: list

    # 扩展后转化成和图片尺寸一样的编码图
    __initial_extreme_seed: np.ndarray
    __contours: tuple
    iniSegProb: np.ndarray

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.scribbles = []
        self.cur_scribble_type = SCRIBBLE_TYPE.SEED
        self.__extrem_pos = []
        self.__contours = ()
        self.__initialseg_end = False

    def imgShape(self):
        return (self.__imgH, self.__imgW)

    @property
    def iniExtremSeed(self):
        return self.__initial_extreme_seed

    @iniExtremSeed.setter
    def iniExtremSeed(self, x):
        self.__initial_extreme_seed = x

    @property
    def extremPos(self):
        return self.__extrem_pos

    def start(self, x, y, color):
        '''
        鼠标按下时调用的方法,x,y为相对于窗口左上角的坐标
        :param x:
        :param y:
        :param color:
        :return:
        '''
        xr, yr = self.mapToRelative(x, y)
        xr, yr = self.validate(xr, yr)

        if self.__initialseg_end:
            Model.Scribble.ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).start(xr, yr, color)
            Model.Scribble.ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).update(xr, yr)
        else:
            self.__extrem_pos.append((xr, yr))

    def validate(self, x, y):
        '''
        如果滑到了图片框之外，让他回到图片上
        :param x:
        :param y:
        :return:
        '''
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x >= self.__imgW:
            x = self.__imgW
        if y >= self.__imgH:
            y = self.__imgH
        return x, y

    def update(self, x, y):
        xr, yr = self.mapToRelative(x, y)
        xr, yr = self.validate(xr, yr)
        if self.__initialseg_end:
            Model.Scribble.ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).update(xr, yr)
        else:
            self.__extrem_pos.append((xr, yr))

    def draw(self, painter: QPainter):
        '''
        用指定SCRIBBLE_TYPE枚举类中的self.cur_scribble_type工具绘制,这里采用的工厂模式,扩展时需要在SCRIBBLE_TYPE添加对应的枚举项、
        并修改ScribeFactory，注意工具类必须继承自Scribblebase，并实现对应的方法，绘制时统一调用其draw方法
        :param painter:
        :return:
        '''
        Model.Scribble.ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).draw(painter)
        painter.setPen(QPen(Qt.darkCyan, 4))
        for p in self.__extrem_pos:
            xr, yr = self.recoverToAbs(p[0], p[1])
            painter.drawPoint(QPoint(xr, yr))
        # if self.__initialseg_end:
        #     ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).draw(painter)
        # else:
        #     painter.setPen(QPen(Qt.darkCyan, 4))
        #     for p in self.__extrem_pos:
        #         xr, yr = self.recoverToAbs(p[0], p[1])
        #         painter.drawPoint(QPoint(xr, yr))

    def end(self, x, y):
        '''
        这里是鼠标放下时调用的方法，鼠标放下代表此次绘制结束，x,y为相对于窗口左上角的坐标
        :param x:
        :param y:
        :return:
        '''
        xr, yr = self.mapToRelative(x, y)
        xr, yr = self.validate(xr, yr)
        if self.__initialseg_end:
            Model.Scribble.ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).end(xr, yr)
        else:
            self.__extrem_pos.append((xr, yr))

    def setImage(self, img: QImage):
        self.rawImage = img
        self.clear()
        self.__imgH = img.height()
        self.__imgW = img.width()
        self.grayImage = QImageToGrayCvMat(img)

    def moveToRefine(self):
        self.__initialseg_end = True

    def computeOrigin(self, framW, framH):
        '''
        label的长宽会根据窗口调整，每次调整后重新计算图片左上角的坐标
        :param framW:label框的宽度
        :param framH: label框的长度
        :return:
        '''
        self.__originX = (framW - self.__imgW) / 2
        self.__originY = (framH - self.__imgH) / 2

    @Slot()
    def clear(self):
        Model.Scribble.ScribeFactory.release()
        self.__initialseg_end = False
        self.__contours = ()
        self.__extrem_pos.clear()
        self.resetImage.emit(self.rawImage)

    def stage1End(self):
        return self.__initialseg_end

    def showContours(self, contours) -> tuple:
        self.__contours = contours
        img = QImageToCvMat(self.rawImage)
        img = cv2.drawContours(
            img, self.__contours, -1, (0, 255, 0), 2)
        q_img = QImage(img.data, img.shape[1], img.shape[0], img.shape[1] * 4, QImage.Format_RGB32)
        self.resetImage.emit(q_img)

    def saveMask(self, filepath):
        if not self.__initialseg_end or len(self.__contours) == 0:
            QMessageBox.warning(None, "warn",
                                "segmentation result not found.")

            return
        img = QImageToCvMat(self.rawImage)
        img = cv2.drawContours(
            img, self.__contours, -1, (0, 255, 0), 2)
        q_img = QImage(img.data, img.shape[1], img.shape[0], img.shape[1] * 4, QImage.Format_RGB32)
        q_img.save(filepath)

    def mapToRelative(self, x, y):
        '''
        相对于父widget(label)左上角坐标转换成相对于图片左上角的坐标
        :param x:
        :param y:
        :return:
        '''
        return x - self.__originX, y - self.__originY

    def recoverToAbs(self, x, y):
        '''
        绘制点的时候，draw接口需要转化会相对与窗口父widget的坐标
        :param x:
        :param y:
        :return:
        '''
        return x + self.__originX, y + self.__originY
