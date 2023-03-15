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
        # 上一次记录上一次打开时的文件夹路径
        self.lastOpenDir = os.path.abspath("Res/test")
        # 获取QImage所能够读取和处理的文件扩展名，作为文件选择窗口的过滤器
        # 当前值为:Image Files(*.bmp *.cur *.gif *.icns *.ico *.jpeg *.jpg *.pbm *.pgm *.png *.ppm *.svg *.svgz *.tga *.tif *.tiff *.wbmp *.webp *.xbm *.xpm)

        self.supportType = "Image Files(" + \
                           " ".join([f"*.{(bytes.decode(bytes(i)))}"
                                     for i in QImageReader.supportedImageFormats()]) + ")"

    @property
    def imgModel(self):
        return self.__img_vm

    @imgModel.setter
    def imgModel(self, m):
        self.__img_vm = m


if __name__ == '__main__':
    print("Image Files(" + " ".join([f"*.{(bytes.decode(bytes(i)))}"
                                     for i in QImageReader.supportedImageFormats()]) + ")")
