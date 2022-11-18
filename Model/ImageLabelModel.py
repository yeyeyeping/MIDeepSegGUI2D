
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QObject
from PySide6.QtCore import Slot
from Model.Scribble import ScribeFactory, SCRIBBLE_TYPE



class ImageLabelModel(QObject):
    __m_parent = None
    # 图片左上角相对与Qlabel左上角的偏移
    __originX: int
    __originY: int
    # Qlabel内显示的图片的长度和宽度，用于计算左上角的坐标
    __imgW: int
    __imgH: int
    showImag: QImage

    cur_scribble_type: SCRIBBLE_TYPE
    scribbles: list

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.scribbles = []

        self.cur_scribble_type = SCRIBBLE_TYPE.SEED

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


    @Slot()
    def clear(self):
        ScribeFactory.release()

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
