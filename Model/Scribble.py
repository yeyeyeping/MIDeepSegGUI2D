from abc import ABC, abstractmethod
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QRect, QPoint
from typing import List
import enum


class SCRIBBLE_TYPE(enum.Flag):
    RECT = 1
    SEED = 2


class Point:
    # x: int
    # y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"x:{self.x}, y:{self.y}"


class Rect:
    '''
    用于存储绘制时的矩形框数据
    包含左上角、右下角相对与图片左上角坐标
    以及绘制时的颜色、像素宽度
    '''
    start: Point
    end: Point
    color: None
    width: int

    def __init__(self, x, y, width=6, color=Qt.red):
        self.start = Point(x, y)
        self.color = color
        self.width = width

    def setEnd(self, x, y):
        self.end = Point(x, y)

    def __repr__(self):
        return f"start point:{self.start}, end point:{self.end}," \
               f" color:{self.color}, width:{self.width}"


class ScribeBase(ABC):

    @abstractmethod
    def start(self, x, y, color):
        pass

    @abstractmethod
    def update(self, x, y):
        pass

    @abstractmethod
    def draw(self, painter: QPainter):
        pass

    @abstractmethod
    def end(self, x, y):
        pass

    @abstractmethod
    def clear(self):
        pass


class PointList(ScribeBase):
    '''
    用“毛笔”（点）工具绘制时，鼠标按下后将会把鼠标经过的位置全部存储到__positive，__negative中
    '''
    __positive: list
    __negative: list
    color: int

    def __init__(self, label_model):
        super().__init__()
        self.__label_model = label_model
        self.__negative = []
        self.__positive = []

    @property
    def negative(self):
        return self.__negative

    @property
    def positive(self):
        return self.__positive

    def start(self, x, y, color):
        self.color = color
        if color == Qt.red:
            self.__positive.append((x, y))
        elif color == Qt.blue:
            self.__negative.append((x, y))

    def update(self, x, y):
        if self.color == Qt.red:
            self.__positive.append((x, y))
        elif self.color == Qt.blue:
            self.__negative.append((x, y))

    def draw(self, painter: QPainter, width=4):
        painter.setPen(QPen(Qt.blue, width))
        for p in self.__negative:
            xr, yr = self.__label_model.recoverToAbs(p[0], p[1])
            painter.drawPoint(QPoint(xr, yr))

        painter.setPen(QPen(Qt.red, width))
        for p in self.__positive:
            xr, yr = self.__label_model.recoverToAbs(p[0], p[1])
            painter.drawPoint(QPoint(xr, yr))

    def end(self, x, y):
        self.update(x, y)

    def clear(self):
        self.__negative.clear()
        self.__positive.clear()


class RectList(ScribeBase):
    __rects: List[Rect]
    curRect: Rect
    __label_model = None

    def __init__(self, label_model):
        super().__init__()
        self.__rects = []
        self.curRect = None
        self.__label_model = label_model

    def start(self, x, y, color=Qt.red, width=4):
        self.curRect = Rect(x, y, width, color)

    def update(self, x, y):
        self.curRect.setEnd(x, y)

    def getRect(self):
        return self.__rects

    def draw(self, painter: QPainter):
        if self.curRect is None:
            return
        # 鼠标按下时，将起点记录到self.curRect,鼠标拖动时将不断的更新curRect的终点
        # 绘制时，将坐标恢复到相对于窗口的左上角
        sxr, syr = self.__label_model.recoverToAbs(self.curRect.start.x, self.curRect.start.y)
        exr, eyr = self.__label_model.recoverToAbs(self.curRect.end.x, self.curRect.end.y)

        painter.setPen(QPen(self.curRect.color, self.curRect.width))
        # 利用QRect：左上角坐标x,y,长，宽绘制
        painter.drawRect(QRect(sxr, syr, exr - sxr, eyr - syr))

        for rect in self.__rects:
            sxr, syr = self.__label_model.recoverToAbs(rect.start.x, rect.start.y)
            exr, eyr = self.__label_model.recoverToAbs(rect.end.x, rect.end.y)
            painter.setPen(QPen(self.curRect.color, self.curRect.width))
            painter.drawRect(QRect(sxr, syr, exr - sxr, eyr - syr))

    def clear(self):
        self.curRect = None
        self.__rects.clear()

    def end(self, x, y):
        self.curRect.setEnd(x, y)
        self.__rects.append(self.curRect)


class ScribeFactory:
    rectList: None
    pointList: None

    @staticmethod
    def getRectList(model_view) -> RectList:
        if not hasattr(ScribeFactory, "rectList"):
            ScribeFactory.rectList = RectList(model_view)
        return ScribeFactory.rectList

    @staticmethod
    def getPointList(model_view) -> PointList:
        if not hasattr(ScribeFactory, "pointList"):
            ScribeFactory.pointList = PointList(model_view)
        return ScribeFactory.pointList

    @staticmethod
    def getScribbleByEnum(t: SCRIBBLE_TYPE, model_view):
        if t == SCRIBBLE_TYPE.RECT:
            return ScribeFactory.getRectList(model_view)
        elif t == SCRIBBLE_TYPE.SEED:
            return ScribeFactory.getPointList(model_view)

    @staticmethod
    def release():
        if hasattr(ScribeFactory, "rectList"):
            ScribeFactory.rectList.clear()
        if hasattr(ScribeFactory, "pointList"):
            ScribeFactory.pointList.clear()


if __name__ == '__main__':

    print(QPainter().device())
