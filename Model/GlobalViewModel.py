from typing import Optional

import PySide6.QtCore
from PySide6.QtCore import QObject
from Model.ImageLabelModel import ImageLabelModel


class GlobalViewModel(QObject):
    __img_vm: ImageLabelModel = None

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__img_vm = ImageLabelModel()

    @property
    def img_vm(self):
        return self.__img_vm

    @img_vm.setter
    def img_vm(self, m):
        self.__img_vm = m
