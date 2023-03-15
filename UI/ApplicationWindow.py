import os
import PySide6
from PySide6.QtCore import QDir
from PySide6 import QtGui
from PySide6.QtGui import QAction, QIcon, QPalette, QFont
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import QImageReader
from Model.GlobalViewModel import GlobalViewModel
from Logic.Common.ImageDelegate import ImageDelegate
from UI.Component.LabelImage import LabelImage
from Logic.utils.Pathdb import get_resource_path
from Logic.Common.MainApplication import MainApplication
from UI.MaskSaveWidget import MaskSaveWidget


class ApplicationWindow(QMainWindow):
    __mainApplication: MainApplication
    img_name: str

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.globalModel = GlobalViewModel()
        self.__mainApplication = MainApplication(self.globalModel)
        self.initUI()

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.xPos.setText(str(event.x()))
        self.yPos.setText(str(event.y()))

    def initUI(self):
        self.setWindowTitle('交互式医学图像标注系统')
        # self.setMaximumSize(600, 450)
        '''设置菜单栏'''

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        # 文件菜单
        self.openAction = QAction(QIcon(get_resource_path("Res/Image/open.bmp")), '打开图片', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('选择一个要标注的图像.')
        self.openAction.triggered.connect(self.on_open)
        fileMenu.addAction(self.openAction)

        # 保存菜单项
        self.saveAction = QAction(QIcon(get_resource_path("Res/Image/save.bmp")), '保存分割结果', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('将分割结果保存到磁盘中')
        self.saveAction.triggered.connect(self.on_save)
        fileMenu.addAction(self.saveAction)

        # 关闭菜单项
        self.closeAction = QAction(QIcon(get_resource_path("Res/Image/exit.bmp")), '退出', self)
        self.closeAction.setShortcut('Ctrl+Q')
        self.closeAction.setStatusTip('退出程序')
        self.closeAction.triggered.connect(self.close)
        fileMenu.addAction(self.closeAction)

        '''设置界面的中心组件'''
        # 设置centerWidget
        self.centerWidget = QWidget(self)
        mainvlayout = QVBoxLayout()
        self.centerWidget.setLayout(mainvlayout)

        hlbox = QHBoxLayout()

        hlbox.addStretch(10)
        self.labelInputDir = QLabel()
        self.labelInputDir.setText("工作目录：")
        hlbox.addWidget(self.labelInputDir)
        hlbox.addStretch(10)
        self.editFileList = QLineEdit()
        self.editFileList.setFixedHeight(30)
        self.editFileList.setMinimumWidth(600)
        self.editFileList.setFocusPolicy(Qt.NoFocus)
        hlbox.addWidget(self.editFileList)
        hlbox.addStretch(10)
        self.annotationButton = QPushButton("加载输入路径")
        self.annotationButton.setStyleSheet("background-color:white")
        self.annotationButton.clicked.connect(self.on_open)
        hlbox.addWidget(self.annotationButton)
        mainvlayout.addLayout(hlbox)

        hlbox2 = QHBoxLayout()

        hlbox2.addStretch(10)
        self.labelOutputDir = QLabel()
        self.labelOutputDir.setText("输出目录：")
        hlbox2.addWidget(self.labelOutputDir)
        hlbox2.addStretch(10)
        self.editFileList2 = QLineEdit()
        self.editFileList2.setFixedHeight(30)
        self.editFileList2.setMinimumWidth(600)
        self.editFileList2.setFocusPolicy(Qt.NoFocus)
        hlbox2.addWidget(self.editFileList2)
        hlbox2.addStretch(10)
        self.annotationButton2 = QPushButton("加载输出路径")
        self.annotationButton2.setStyleSheet("background-color:white")
        self.annotationButton2.clicked.connect(self.on_open_output)
        hlbox2.addWidget(self.annotationButton2)
        mainvlayout.addLayout(hlbox2)

        self.fileListView = QListView(self)
        self.fileListView.setMinimumWidth(100)
        self.fileListView.setMinimumHeight(200)
        self.fileModel = QFileSystemModel(self)
        # self.fileListView.selectionChanged
        self.fileListView.selectionChanged = self.on_selection_changed
        self.fileModel.setIconProvider(QFileIconProvider())
        self.fileModel.setFilter(QDir.Files)
        self.fileModel.setNameFilters(["*." + str(i, encoding="utf8") for i in QImageReader.supportedImageFormats()])
        self.fileModel.setNameFilterDisables(False)

        self.fileListView.setMouseTracking(True)

        hLayout = QHBoxLayout()
        mainvlayout.addLayout(hLayout)
        hLayout.addWidget(self.fileListView)

        hLayout.addStretch(10)

        # 布局左边的图片框
        self.img = LabelImage(self)
        self.img.initialize(self.globalModel)
        self.img.setStyleSheet("border:3px solid #242424;")
        # self.img.setPixmap(get_resource_path("Res/Image/logo.png"))
        self.img.setMinimumWidth(450)
        self.img.setMinimumHeight(450)
        hLayout.addWidget(self.img)
        hLayout.addStretch(10)
        # 右边的标签和按钮，放在一个QWidget里面
        self.container = QWidget(self.centerWidget)
        hLayout.addWidget(self.container)

        vLayout = QVBoxLayout()
        self.container.setLayout(vLayout)

        self.methodLine = QLabel(self)
        palette = QPalette()
        palette.setColor(self.methodLine.foregroundRole(), Qt.blue)
        tipsFont = self.methodLine.font()
        tipsFont.setPointSize(10)
        self.methodLine.setText("分割")
        self.methodLine.setPalette(palette)
        self.methodLine.setFixedHeight(30)
        self.methodLine.setWordWrap(True)
        self.methodLine.setFont(tipsFont)
        vLayout.addWidget(self.methodLine)

        self.segmentButton = QPushButton("粗分割")
        self.segmentButton.setStyleSheet("background-color:white")
        self.segmentButton.clicked.connect(self.__mainApplication.extremSegmentation)
        vLayout.addWidget(self.segmentButton)

        self.refinementButton = QPushButton("修正")
        self.refinementButton.setStyleSheet("background-color:white")
        self.refinementButton.clicked.connect(self.__mainApplication.refine)
        vLayout.addWidget(self.refinementButton)

        vLayout.addStretch(10)

        self.saveLine = QLabel(self)
        self.saveLine.setText("清除或保存")
        self.saveLine.setPalette(palette)
        self.saveLine.setFixedHeight(30)
        self.saveLine.setWordWrap(True)
        self.saveLine.setFont(tipsFont)
        vLayout.addWidget(self.saveLine)

        self.cleanButton = QPushButton("清除所有点击")
        self.cleanButton.setStyleSheet("background-color:white")
        self.cleanButton.clicked.connect(self.globalModel.imgModel.clear)
        vLayout.addWidget(self.cleanButton)

        self.nextButton = QPushButton("保存分割结果")
        self.nextButton.setStyleSheet("background-color:white")
        self.nextButton.clicked.connect(self.on_save)
        vLayout.addWidget(self.nextButton)
        vLayout.addStretch(10)
        pos = QLabel("鼠标位置：")
        pos.setPalette(palette)
        vLayout.addWidget(pos)
        self.xPosContainer = QHBoxLayout()
        self.xPos = QLineEdit()
        self.xPos.setFixedHeight(30)
        self.xPos.setFixedWidth(70)
        self.xlabel = QLabel("x：")
        self.xPosContainer.addWidget(self.xlabel)
        self.xPosContainer.addWidget(self.xPos)
        vLayout.addLayout(self.xPosContainer)

        self.yPosContainer = QHBoxLayout()
        self.yPos = QLineEdit()
        self.yPos.setFixedHeight(30)
        self.yPos.setFixedWidth(70)
        self.ylabel = QLabel("y：")
        self.yPosContainer.addWidget(self.ylabel)
        self.yPosContainer.addWidget(self.yPos)
        vLayout.addLayout(self.yPosContainer)

        self.auxWidget = MaskSaveWidget()
        self.auxWidget.resultSignal.connect(self.handle_save)
        self.auxWidget.setWindowModality(Qt.WindowModality.ApplicationModal)
        ApplicationWindow.center(self.auxWidget)
        vLayout.addStretch(1)
        self.setCentralWidget(self.centerWidget)
        self.centerWidget.setMouseTracking(True)
        self.center()
        self.show()

    @Slot()
    def handle_save(self, ok, p):
        if not ok:
            self.auxWidget.close()
            return
        if ok and self.__mainApplication.saveMask(p):
            QMessageBox.warning(None, "提示", "保存成功")
            idx = self.fileListView.selectionModel().currentIndex()
            newidx = idx.siblingAtRow(idx.row() + 1)
            if not newidx.isValid():
                QMessageBox.warning(self, "警告",
                                    "标注完成")
                return
            selectmodel = self.fileListView.selectionModel()
            selectmodel.setCurrentIndex(newidx, QItemSelectionModel.SelectionFlag.ToggleCurrent)
            self.auxWidget.close()
        else:
            QMessageBox.warning(None, "警告", "保存失败")
        return

    @Slot()
    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        # 获取当前选择的项
        if QItemSelection.isEmpty(selected):
            return
        fname = selected.indexes()[0].data()
        fpath = os.path.join(self.dirpath, fname)

        self.img_name = os.path.basename(fpath)
        self.img.setPixmap(fpath)

    @Slot()
    def on_open_output(self):
        delegate = ImageDelegate(self.globalModel)
        dirpath = delegate.selectDir(win=self.parent())
        if not os.path.exists(dirpath):
            return
        self.outputdir = dirpath
        self.editFileList2.setText(self.outputdir)
        first_row = self.fileModel.index(0, 0, self.fileListView.rootIndex())
        self.fileListView.setCurrentIndex(first_row)

    @Slot()
    def on_open(self):
        delegate = ImageDelegate(self.globalModel)
        dirpath = delegate.selectDir(win=self.parent())
        if not os.path.exists(dirpath):
            return
        self.fileListView.setModel(self.fileModel)
        self.fileModel.setRootPath(dirpath)
        self.dirpath = dirpath
        self.editFileList.setText(self.dirpath)
        self.fileListView.setRootIndex(self.fileModel.index(dirpath))

    @Slot()
    def on_save(self):
        if not hasattr(self, "img_name"):
            QMessageBox.warning(self, "警告",
                                "您还没有选择文件")
            return
        raimage = self.globalModel.imgModel.getRawImage()
        mask = self.globalModel.imgModel.getMask()
        self.auxWidget.updateCom(raimage, mask, os.path.join(self.outputdir, "mask_" + self.img_name))
        self.auxWidget.show()
        # if not self.__mainApplication.saveMask(self.outputdir, self.img_name):
        #     return
        # idx = self.fileListView.selectionModel().currentIndex()
        # selectmodel = self.fileListView.selectionModel()
        # # selectmodel.clear()
        # newidx = idx.siblingAtRow(idx.row() + 1)
        # if not newidx.isValid():
        #     QMessageBox.warning(self, "警告",
        #                         "标注完成")
        #     return
        # selectmodel.setCurrentIndex(newidx, QItemSelectionModel.SelectionFlag.ToggleCurrent)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    if __name__ == '__main__':
        print()
