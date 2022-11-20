from PySide6.QtWidgets import QFileDialog
from Model.GlobalViewModel import GlobalViewModel


class ImageDelegate:
    def __init__(self, gvm: GlobalViewModel):
        self.gvm = gvm

    def selectFile(self, win):
        fdiag = QFileDialog()
        f = fdiag.getOpenFileName(win, "Open File",
                                  self.gvm.lastOpenDir,
                                  self.gvm.supportType
                                  )
        fdiag.setStyleSheet("")
        return f[0]

    def selectSavePath(self, win):
        f = QFileDialog.getSaveFileName(win,
                                        "Save File",
                                        self.gvm.lastOpenDir,
                                        self.gvm.supportType
                                        )
        return f[0]
