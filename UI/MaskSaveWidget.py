# -*- coding: utf-8 -*-
import os

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, Slot


class MaskSaveWidget(QWidget):
    resultSignal = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # self.setWindowModality(Qt.WindowModality.ApplicationModal)
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        hbox = QHBoxLayout()
        self.imgRawImage = QLabel()
        self.imgRawImage.setMaximumWidth(300)
        self.imgRawImage.setMaximumHeight(300)

        hbox.addStretch(20)
        self.imgMask = QLabel()
        self.imgMask.setMaximumWidth(300)
        self.imgMask.setMaximumHeight(300)
        hbox.addWidget(self.imgRawImage)
        hbox.addWidget(self.imgMask)
        vbox.addLayout(hbox)

        hPathLayout = QHBoxLayout()
        hPathLayout.addWidget(QLabel("文件名："))
        self.path = QLineEdit()
        hPathLayout.addWidget(self.path)
        vbox.addLayout(hPathLayout)

        buttonLayout = QHBoxLayout()
        vbox.addLayout(buttonLayout)

        buttonLayout.addStretch(50)
        self.pushButtonYes = QPushButton("确定")
        self.pushButtonYes.clicked.connect(self.yesButtonHandle)
        self.pushButtonNo = QPushButton("取消")
        self.pushButtonNo.clicked.connect(self.noButtonHandle)
        buttonLayout.addWidget(self.pushButtonYes)
        buttonLayout.addStretch(20)
        buttonLayout.addWidget(self.pushButtonNo)
        buttonLayout.addStretch(50)

    def updateCom(self, raw, mask, savepath):
        self.imgRawImage.setPixmap(raw)
        self.imgMask.setPixmap(mask)
        self.path.setText(savepath)

    @Slot()
    def yesButtonHandle(self):
        if not os.path.exists(os.path.dirname(self.path.text())):
            QMessageBox.warning(self, "warn", "路径不正确")
        self.resultSignal.emit(True, self.path.text())

    @Slot()
    def noButtonHandle(self):
        self.resultSignal.emit(False, "")


if __name__ == '__main__':
    import sys

    app = QApplication()
    main = MaskSaveWidget()
    main.show()
    sys.exit(app.exec())
