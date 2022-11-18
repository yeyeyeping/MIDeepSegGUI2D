from typing import Optional
import os
from PySide6.QtCore import QObject
from PySide6.QtGui import QImageReader

from Model.ImageLabelModel import ImageLabelModel


class GlobalViewModel(QObject):
    __img_vm: ImageLabelModel
    lastOpenDir: str
    supportType: str

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.__img_vm = ImageLabelModel(self)
        self.lastOpenDir = os.path.abspath(".")
        self.supportType = "Images" + str(
            tuple([f"*.{(bytes.decode(bytes(i)))}"
                   for i in QImageReader.supportedImageFormats()]))

    @property
    def img_vm(self):
        return self.__img_vm

    @img_vm.setter
    def img_vm(self, m):
        self.__img_vm = m
