from abc import ABC, abstractmethod
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QRect
from typing import List
import enum


class SCRIBBLE_TYPE(enum.Flag):
    RECT = 1
    SEED = 2


class Point:
    x: int
    y: int
    color: None

    def __init__(self, x, y, color=Qt.red):
        self.x = x
        self.y = y
        self.color = color

    def __repr__(self):
        return f"x:{self.x}, y:{self.y}"


class Rect:
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
    def __init__(self, label_model):
        super().__init__()
        self.__label_model = label_model

    def start(self, x, y, color):
        pass

    def update(self, x, y):
        pass

    def draw(self, painter: QPainter):
        pass

    def end(self, x, y):
        pass

    def clear(self):
        pass


class RectList(ScribeBase):
    __rects: List[Rect]
    curRect: Rect
    __label_model = None

    def __init__(self, label_model):
        super().__init__()
        self.__rects = []
        self.curRect = None
        self.__label_model = label_model

    def start(self, x, y, color=Qt.red, width=6):
        self.curRect = Rect(x, y, width, color)

    def update(self, x, y):
        self.curRect.setEnd(x, y)

    def getRect(self):
        return self.__rects

    def draw(self, painter: QPainter):
        if self.curRect is None:
            return
        sxr, syr = self.__label_model.recoverToAbs(self.curRect.start.x, self.curRect.start.y)
        exr, eyr = self.__label_model.recoverToAbs(self.curRect.end.x, self.curRect.end.y)

        painter.setPen(QPen(self.curRect.color, self.curRect.width))
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
            ScribeFactory.pointList = RectList(model_view)
        return ScribeFactory.pointList

    @staticmethod
    def getScribbleByEnum(t: SCRIBBLE_TYPE, model_view):
        if t == SCRIBBLE_TYPE.RECT:
            return ScribeFactory.getRectList(model_view)
        elif t == SCRIBBLE_TYPE.SEED:
            return ScribeFactory.getPointList(model_view)


if __name__ == '__main__':
    print(QPainter().device())
