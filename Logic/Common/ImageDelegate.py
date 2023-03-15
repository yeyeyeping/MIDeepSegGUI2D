import os

from PySide6.QtWidgets import QFileDialog
from Model.GlobalViewModel import GlobalViewModel


class ImageDelegate:
    def __init__(self, gvm: GlobalViewModel):
        self.gvm = gvm
    def selectDir(self,win):
        fdiag = QFileDialog(win)
        fdiag.setStyleSheet("")
        f = fdiag.getExistingDirectory(win,"选择目录", self.gvm.lastOpenDir)
        return f
    def selectFile(self, win):
        fdiag = QFileDialog()
        f = fdiag.getOpenFileName(win, "打开文件",
                                  self.gvm.lastOpenDir,
                                  self.gvm.supportType
                                  )
        fdiag.setStyleSheet("")
        return f[0]

    def selectSavePath(self, win, filename):
        name, exet = filename.split(".")[0], filename.split(".")[1],
        f = QFileDialog.getSaveFileName(win,
                                        "Save File",
                                        os.path.join(self.gvm.lastOpenDir, f"{name}_mask.{exet}"),
                                        self.gvm.supportType
                                        )
        return f[0]
