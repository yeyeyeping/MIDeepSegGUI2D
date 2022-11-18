import enum

from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from Model.Scribble import RectList, PointList, ScribeFactory, SCRIBBLE_TYPE


class SEED_TYPE(enum.Flag):
    No = -1
    POSITIVE = 0
    NEGATIVE = 1


class ImageLabelModel(QObject):
    __m_parent = None
    __backgound_seed: list
    __foreground_seed: list
    # 图片左上角相对与Qlabel左上角的偏移
    __originX: int
    __originY: int
    # Qlabel内显示的图片的长度和宽度，用于计算左上角的坐标
    __imgW: int
    __imgH: int
    showImag: QImage
    seed_type: SEED_TYPE

    cur_scribble_type: SCRIBBLE_TYPE
    scribbles: list

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__foreground_seed = []
        self.__backgound_seed = []
        self.seed_type = SEED_TYPE.No
        self.scribbles = []

        self.scribbles.append(RectList(self))
        self.scribbles.append(PointList(self))

        self.cur_scribble_type = SCRIBBLE_TYPE.RECT

    def start(self, x, y, color):
        xr, yr = self.mapToRelative(x, y)
        ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).start(xr, yr, color)
        ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).update(xr, yr)

    def update(self, x, y):
        xr, yr = self.mapToRelative(x, y)
        ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).update(xr, yr)

    def draw(self, painter: QPainter):
        ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).draw(painter)

    def end(self, x, y):
        xr, yr = self.mapToRelative(x, y)
        ScribeFactory.getScribbleByEnum(self.cur_scribble_type, self).end(xr, yr)

    @property
    def backgroundSeed(self):
        return self.__backgound_seed

    @property
    def foregoundSeed(self):
        return self.__foreground_seed

    def setImage(self, img: QImage):
        self.clear()
        self.__imgH = img.height()
        self.__imgW = img.width()
        self.showImag = img

    def computeOrigin(self, framW, framH):
        '''
        label的长宽会根据窗口调整，每次调整后重新计算图片左上角的坐标
        :param framW:label框的宽度
        :param framH: label框的长度
        :return:
        '''
        self.__originX = (framW - self.__imgW) / 2
        self.__originY = (framH - self.__imgH) / 2

    def addPositiveSeed(self, x, y):
        '''
        TODO:
            如果如需实现划线、画框、画圆，此方法可以移除
        '''
        xr, yr = self.mapToRelative(x, y)
        if xr < 0 or yr < 0:
            return
        self.__foreground_seed.append((xr, yr))

    def addNativeSeed(self, x, y):
        '''
        TODO:
            如果如需实现划线、画框、画圆，此方法可以移除
        '''
        xr, yr = self.mapToRelative(x, y)
        if xr < 0 or yr < 0:
            return
        self.__backgound_seed.append((xr, yr))

    @Slot()
    def clear(self):
        self.__backgound_seed.clear()
        self.__foreground_seed.clear()

    def mapToRelative(self, x, y):
        '''
        相对于窗口左上角坐标转换成相对于图片左上角的坐标
        :param x:
        :param y:
        :return:
        '''
        return x - self.__originX, y - self.__originY

    def recoverToAbs(self, x, y):
        '''
        绘制点的时候，draw接口需要转化会相对与窗口左上角的坐标
        :param x:
        :param y:
        :return:
        '''
        return x + self.__originX, y + self.__originY
