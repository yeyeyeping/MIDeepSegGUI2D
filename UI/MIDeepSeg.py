from PySide6.QtGui import QAction, QIcon, QPixmap, QImage, QPalette
from PySide6.QtWidgets import *
from PySide6.QtCore import *


class MIDeepSeg(QMainWindow):

    def __init__(self):
        super().__init__()
        '''
        self.graph_maker = Controler()
        '''
        self.seed_type = 1  # annotation type
        self.all_datasets = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MIDeepSeg')
        # self.setMaximumSize(600, 450)
        # 设置菜单项
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        # 文件菜单
        self.openAction = QAction(QIcon('exit24.png'), 'Open Image', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open a file for segmenting.')
        self.openAction.triggered.connect(self.on_open)
        fileMenu.addAction(self.openAction)
        # 保存菜单项
        self.saveAction = QAction(QIcon('exit24.png'), 'Save Image', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save file to disk.')
        self.saveAction.triggered.connect(self.on_save)
        fileMenu.addAction(self.saveAction)
        # 关闭菜单项
        self.closeAction = QAction(QIcon('exit24.png'), 'Exit', self)
        self.closeAction.setShortcut('Ctrl+Q')
        self.closeAction.setStatusTip('Exit application')
        self.closeAction.triggered.connect(self.on_close)
        fileMenu.addAction(self.closeAction)

        self.mainWidget = QWidget(self)
        self.hLayout = QHBoxLayout(self.mainWidget)
        # 布局左边的图片框
        # 由于图片框有鼠标进入和移除的事件，这里可能需要重构
        # 左边的标签和按钮
        self.seedLabel = QLabel()
        self.seedLabel.setStyleSheet("border:3px solid #242424;")
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.seeds))))
        self.seedLabel.setAlignment(Qt.AlignCenter)
        self.seedLabel.mousePressEvent = self.mouse_down
        self.seedLabel.mouseMoveEvent = self.mouse_drag
        self.hLayout.addWidget(self.seedLabel)

        self.container = QWidget()
        self.hLayout.addWidget(self.container)

        self.vLayout = QVBoxLayout(self.container)
        self.stateLine = QLabel()
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
        self.vLayout.addWidget(self.stateLine)

        self.annotationButton = QPushButton("Load Image")
        self.annotationButton.setStyleSheet("background-color:white")
        self.annotationButton.clicked.connect(self.on_open)
        self.vLayout.addWidget(self.annotationButton)

        self.methodLine = QLabel()
        self.methodLine.setText("Segmentation.")
        self.methodLine.setPalette(palette)
        self.methodLine.setFixedHeight(30)
        self.methodLine.setWordWrap(True)
        self.methodLine.setFont(tipsFont)
        self.vLayout.addWidget(self.methodLine)

        self.segmentButton = QPushButton("Segment")
        self.segmentButton.setStyleSheet("background-color:white")
        self.segmentButton.clicked.connect(self.on_segment)
        self.vLayout.addWidget(self.segmentButton)

        self.refinementButton = QPushButton("Refinement")
        self.refinementButton.setStyleSheet("background-color:white")
        self.refinementButton.clicked.connect(self.on_refinement)
        self.vLayout.addWidget(self.refinementButton)

        self.saveLine = QLabel()
        self.saveLine.setText("Clean or Save.")
        self.saveLine.setPalette(palette)
        self.saveLine.setFixedHeight(30)
        self.saveLine.setWordWrap(True)
        self.saveLine.setFont(tipsFont)
        self.vLayout.addWidget(self.saveLine)

        self.cleanButton = QPushButton("Clear all seeds")
        self.cleanButton.setStyleSheet("background-color:white")
        self.cleanButton.clicked.connect(self.on_clean)
        self.vLayout.addWidget(self.cleanButton)

        self.nextButton = QPushButton("Save segmentation")
        self.nextButton.setStyleSheet("background-color:white")
        self.nextButton.clicked.connect(self.on_save)
        self.vLayout.addWidget(self.nextButton)

        self.setCentralWidget(self.mainWidget)
        self.show()

    @staticmethod
    def get_qimage(cvimage):
        height, width, bytes_per_pix = cvimage.shape
        bytes_per_line = width * bytes_per_pix
        cv2.cvtColor(cvimage, cv2.COLOR_BGR2RGB, cvimage)
        return QImage(cvimage.data, width, height, bytes_per_line, QImage.Format_RGB888)

    def mouse_down(self, event):
        if event.button() == Qt.LeftButton:
            self.seed_type = 2
        elif event.button() == Qt.RightButton:
            self.seed_type = 3
        self.graph_maker.add_seed(event.x(), event.y(), self.seed_type)
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.seeds))))

    def mouse_drag(self, event):
        self.graph_maker.add_seed(event.x(), event.y(), self.seed_type)
        self.seedLabel.setPixmap(QPixmap.fromImage(
            self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.seeds))))

    @Slot()
    def on_open(self):
        f = QFileDialog.getOpenFileName()
        if f[0] is not None and f[0] != "":
            f = f[0]
            self.graph_maker.load_image(str(f))
            self.seedLabel.setPixmap(QPixmap.fromImage(
                self.get_qimage(self.graph_maker.get_image_with_overlay(self.graph_maker.seeds))))
        else:
            pass

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
    def on_close(self):
        print('Closing')
        self.window.close()

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
