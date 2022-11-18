from PySide6.QtWidgets import QFileDialog

from Model.GlobalViewModel import GlobalViewModel


class ImageDelegate:
    def __init__(self, gvm: GlobalViewModel):
        self.gvm = gvm

    def selectFile(self, win):
        f = QFileDialog.getOpenFileName(win, "Open File",
                                        self.gvm.lastOpenDir,
                                        self.gvm.supportType
                                        )
        return f[0]

    def saveSeg(self, filename):
        '''
        TODO：
        实现导出分割结果
        '''

        pass
