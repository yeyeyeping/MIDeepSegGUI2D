from Model.GlobalViewModel import GlobalViewModel
from Logic.Common.ImageDelegate import ImageDelegate
from PySide6.QtGui import QAction, QIcon, QPixmap, QImage, QPalette, QImageReader
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from UI.Component.LabelImage import LabelImage
from Logic.utils.Pathdb import get_resource_path


class ApplicationWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        '''
        self.graph_maker = Controler()
        '''
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Annotation')
        self.setMaximumSize(600, 450)

        '''设置菜单栏'''
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        # 文件菜单
        self.openAction = QAction(QIcon(get_resource_path("Res/Image/open.bmp")), 'Open Image', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open a file for segmenting.')
        self.openAction.triggered.connect(self.on_open)
        fileMenu.addAction(self.openAction)

        # 保存菜单项
        self.saveAction = QAction(get_resource_path("Res/Image/save.bmp"), 'Save Image', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save file to disk.')
        self.saveAction.triggered.connect(self.on_save)
        fileMenu.addAction(self.saveAction)

        # 关闭菜单项
        self.closeAction = QAction(QIcon(get_resource_path("Res/Image/exit.bmp")), 'Exit', self)
        self.closeAction.setShortcut('Ctrl+Q')
        self.closeAction.setStatusTip('Exit application')
        self.closeAction.triggered.connect(self.close)
        fileMenu.addAction(self.closeAction)

        '''设置界面的中心组件'''
        # 设置centerWidget
        self.centerWidget = QWidget(self)
        hLayout = QHBoxLayout()
        self.centerWidget.setLayout(hLayout)
        self.globalModel = GlobalViewModel()

        # 布局左边的图片框
        self.img = LabelImage(self)
        self.img.initialize(self.globalModel)
        self.img.setStyleSheet("border:3px solid #242424;")
        self.img.setPixmap(get_resource_path("Res/Image/logo.png"))
        hLayout.addWidget(self.img)

        # 右边的标签和按钮，放在一个QWidget里面
        self.container = QWidget(self.centerWidget)
        hLayout.addWidget(self.container)

        vLayout = QVBoxLayout()
        self.container.setLayout(vLayout)
        self.stateLine = QLabel(self)
        self.stateLine.setText("Clicks as user input.")
        # 设置颜色
        palette = QPalette()
        palette.setColor(self.stateLine.foregroundRole(), Qt.blue)
        self.stateLine.setPalette(palette)
        tipsFont = self.stateLine.font()
        tipsFont.setPointSize(10)
        self.stateLine.setFixedHeight(30)
        self.stateLine.setWordWrap(True)
        self.stateLine.setFont(tipsFont)
        vLayout.addWidget(self.stateLine)

        self.annotationButton = QPushButton("Load Image")
        self.annotationButton.setStyleSheet("background-color:white")
        self.annotationButton.clicked.connect(self.on_open)
        vLayout.addWidget(self.annotationButton)

        self.methodLine = QLabel(self)
        self.methodLine.setText("Segmentation.")
        self.methodLine.setPalette(palette)
        self.methodLine.setFixedHeight(30)
        self.methodLine.setWordWrap(True)
        self.methodLine.setFont(tipsFont)
        vLayout.addWidget(self.methodLine)

        self.segmentButton = QPushButton("Segment")
        self.segmentButton.setStyleSheet("background-color:white")
        self.segmentButton.clicked.connect(self.on_segment)
        self.vLayout.addWidget(self.segmentButton)

        self.refinementButton = QPushButton("Refinement")
        self.refinementButton.setStyleSheet("background-color:white")
        self.refinementButton.clicked.connect(self.on_refinement)
        vLayout.addWidget(self.refinementButton)

        self.saveLine = QLabel(self)
        self.saveLine.setText("Clean or Save.")
        self.saveLine.setPalette(palette)
        self.saveLine.setFixedHeight(30)
        self.saveLine.setWordWrap(True)
        self.saveLine.setFont(tipsFont)
        vLayout.addWidget(self.saveLine)

        self.cleanButton = QPushButton("Clear all seeds")
        self.cleanButton.setStyleSheet("background-color:white")
        self.cleanButton.clicked.connect(self.on_clean)
        vLayout.addWidget(self.cleanButton)

        self.nextButton = QPushButton("Save segmentation")
        self.nextButton.setStyleSheet("background-color:white")
        self.nextButton.clicked.connect(self.on_save)
        vLayout.addWidget(self.nextButton)

        self.setCentralWidget(self.centerWidget)
        self.show()

    @staticmethod
    def get_qimage(cvimage):
        height, width, bytes_per_pix = cvimage.shape
        bytes_per_line = width * bytes_per_pix
        cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB, cvimage)
        return QImage(cvimage.data, width, height, bytes_per_line, QImage.Format_RGB888)

    @Slot()
    def on_open(self):
        delegate = ImageDelegate(self.globalModel)
        fpath = delegate.selectFile(win=self)
        self.seedLabel.setPixmap(fpath)

    @Slot()
    def on_save(self):
        f = QFileDialog.getSaveFileName()
        print('Saving')
        if f is not None and f != "":
            f = f[0]
            self.graph_maker.save_image(f)
            self.graph_maker.save_image(f)
        else:
            pass


    @Slot()
    def on_segment(self):
        self.graph_maker.extreme_segmentation()
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.extreme_segmentation))))

    @Slot()
    def on_clean(self):
        self.graph_maker.clear_seeds()
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.clear_seeds))))

    @Slot()
    def on_refinement(self):
        self.graph_maker.refined_seg()
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.refined_seg))))


if __name__ == '__main__':
    print()
