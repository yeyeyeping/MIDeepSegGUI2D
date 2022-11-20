import cv2
import torch.cuda
from PySide6.QtCore import Slot, QObject
from PySide6.QtWidgets import QMessageBox
from skimage import measure
import maxflow

from Logic.Common.ImageDelegate import ImageDelegate
from Logic.Common.BboxCropper import BboxCropper
from Logic.Common.NetworkDelegate import NetworkDelegate
from Logic.Common.network import UNet
from Logic.utils.Pathdb import get_resource_path
from Logic.utils.utils import *
from Model.GlobalViewModel import GlobalViewModel
import Model


class MainApplication(QObject):
    __globalvm: GlobalViewModel
    __network_delegate: NetworkDelegate
    cuda: bool
    crf_param: tuple

    def __init__(self, globavm: GlobalViewModel):
        super(MainApplication, self).__init__()
        self.__globalvm = globavm
        pth = get_resource_path("Res/iter_15000.pth")
        self.cuda = torch.cuda.is_available()
        self.crf_param = (5.0, 0.1)
        self.__network_delegate = NetworkDelegate(self.cuda, UNet(2, 2, 16))
        self.__network_delegate.loadModel(pth)

    @Slot()
    def extremSegmentation(self):
        extreme_pos = self.__globalvm.imgModel.extremPos
        if len(extreme_pos) == 0:
            QMessageBox.warning(None, "warn",
                                "Please provide initial seeds for segmentation.")
            return
        # 将记录鼠标的点击点的位置信息转换到和图片大小一样的单通道矩阵上
        grayImage = self.__globalvm.imgModel.grayImage
        seeds = self.pos2seed(extreme_pos, grayImage.shape)
        # 扩展seeds
        seeds = extends_points(seeds)
        self.__globalvm.imgModel.iniExtremSeed = seeds

        # 根据seed最左、上、右、下四个点 (生成bbox，创建生成bbox区域裁剪器)
        crop = BboxCropper(seeds, self.__globalvm.imgModel.imgShape())

        # 在灰度图、seeds图上裁剪出对应的区域
        cropped_img, cropped_seed = crop.crop1d(grayImage), crop.crop1d(seeds)
        normal_img = itensity_normalization(cropped_img)
        cropped_geos = interaction_geodesic_distance(
            normal_img, cropped_seed)

        # 将剪裁后的图片放大到固定的尺寸(96,96)，堆叠测地线图、原图获得输出
        zoomed_img, zoomed_geos = zoom_image(normal_img, (96, 96)), zoom_image(cropped_geos, (96, 96))
        input = np.asarray([[zoomed_img, zoomed_geos]])

        # 送入网络识别
        prob = self.__network_delegate.inference(input)
        prob = prob.transpose((1, 2, 0))
        fixed_prod = maxflow.maxflow2d(zoomed_img.astype(np.float32), prob, self.crf_param)

        # 将96，96的输出结果放大会原来之前和bbox大小一致
        x, y = cropped_img.shape
        fixed_prod = ndimage.zoom(fixed_prod, (x / 96, y / 96), output=None,
                                  order=0, mode='constant', cval=0.0, prefilter=True)

        pred = np.zeros_like(grayImage, dtype=np.float)
        pred[crop.bbox[0]:crop.bbox[2], crop.bbox[1]:crop.bbox[3]] = fixed_prod

        # 保存副本，用于后续refine
        self.__globalvm.imgModel.iniSegProb = np.array(pred)

        pred[pred >= 0.5] = 1
        pred[pred < 0.5] = 0

        contours = self.findContours(pred)
        self.__globalvm.imgModel.showContours(contours)
        # 第一阶段已经结束设置为false
        self.__globalvm.imgModel.moveToRefine()

    def findContours(self, pred):
        strt = ndimage.generate_binary_structure(2, 1)
        # 开运算 去除噪点
        seg = np.asarray(
            ndimage.morphology.binary_opening(pred, strt), np.uint8)

        # 闭运算 填充空洞
        seg = np.asarray(
            ndimage.morphology.binary_closing(seg, strt), np.uint8)
        seg = ndimage.binary_fill_holes(seg)

        seg = self.largestConnectComponent(seg)
        seg = np.asarray(seg, dtype=np.uint8)
        contours, _ = cv2.findContours(
            seg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def pos2seed(self, extrem_pos, shape):
        seeds = np.zeros(shape)
        # 这里需要注意存的是鼠标x,y和图片数组(高,宽，通道)的区别
        for (x, y) in extrem_pos:
            seeds[int(y), int(x)] = 1
        return seeds

    def largestConnectComponent(self, img):
        binaryimg = img
        label_image, num = measure.label(
            binaryimg, background=0, return_num=True)
        areas = [r.area for r in measure.regionprops(label_image)]
        areas.sort()
        if len(areas) > 1:
            for region in measure.regionprops(label_image):
                if region.area < areas[-1]:
                    for coordinates in region.coords:
                        label_image[coordinates[0], coordinates[1]] = 0
        label_image = label_image.astype(np.int8)
        label_image[np.where(label_image > 0)] = 1
        return label_image

    def extends_points(self, seed):
        if (seed.sum() > 0):
            points = ndimage.distance_transform_edt(seed == 0)
            points[points > 2] = 0
            points[points > 0] = 1
        else:
            points = seed
        return points.astype(np.uint8)

    @Slot()
    def refine(self):
        if not self.__globalvm.imgModel.stage1End():
            return
        grayImage = self.__globalvm.imgModel.grayImage
        # 获取点击的前景点和背景点，编码成图
        label_image_view = self.__globalvm.imgModel
        fg_pos, bg_pos = Model.Scribble.ScribeFactory.getScribbleByEnum(Model.Scribble.SCRIBBLE_TYPE.SEED,
                                                                        label_image_view).positive, \
                         Model.Scribble.ScribeFactory.getScribbleByEnum(Model.Scribble.SCRIBBLE_TYPE.SEED,
                                                                        label_image_view).negative
        fg_seeds, bg_seeds = self.pos2seed(fg_pos, grayImage.shape), \
                             self.pos2seed(bg_pos, grayImage.shape),
        fg_seeds, bg_seeds = extends_points(fg_seeds), \
                             extends_points(bg_seeds)

        # 把前、背景点击图、首次分割使用的extreme seeds求并集，依据这个并集生成裁剪器
        union_seeds = np.maximum(fg_seeds, bg_seeds)
        refined_seeds = np.maximum(union_seeds, self.__globalvm.imgModel.iniExtremSeed)
        cropper = BboxCropper(refined_seeds, self.__globalvm.imgModel.imgShape())

        cropped_img = itensity_standardization(cropper.crop1d(grayImage))

        # 阶段一自动分割产生的概率图产生
        stage1prob = self.__globalvm.imgModel.iniSegProb

        fg_prob = stage1prob
        bg_prob = 1.0 - stage1prob
        cropped_initial_seg = cropper.crop1d(fg_prob)
        cropped_back_seg = cropper.crop1d(bg_prob)

        # 计算前景的测地线 距离图
        cropped_fore_seeds = cropper.crop1d(fg_seeds)
        cropped_fore_geos = interaction_refined_geodesic_distance(
            cropped_img, cropped_fore_seeds)

        # 计算背景的测地线距离图
        cropped_back_seeds = cropper.crop1d(bg_seeds)
        cropped_back_geos = interaction_refined_geodesic_distance(
            cropped_img, cropped_back_seeds)

        # 测地线距离图、第一阶段自动分割结果求并集,fore_prob,back_prob
        fore_prob = np.maximum(cropped_fore_geos, cropped_initial_seg)
        back_prob = np.maximum(cropped_back_geos, cropped_back_seg)

        prob_feature = torch.tensor(np.asarray([back_prob, fore_prob]))
        softmax_feature = torch.softmax(torch.softmax(prob_feature, dim=0), dim=0)
        prob = softmax_feature.permute([1, 2, 0])

        # 合并时避免同一位置出现两个1
        crf_seed = np.asarray([cropped_back_seeds, cropped_fore_seeds])
        crf_seed = np.transpose(crf_seed, [1, 2, 0]).astype(np.uint8)
        crf_seed[cropped_back_seeds & cropped_fore_seeds] = [1, 0]

        # 执行maxflow优化
        refined_pred = maxflow.interactive_maxflow2d(cropped_img, prob, crf_seed, self.crf_param)

        # 预测结果还原成gray尺寸一样
        pred = np.zeros_like(grayImage, dtype=np.float)
        pred[cropper.bbox[0]:cropper.bbox[2], cropper.bbox[1]:cropper.bbox[3]] = refined_pred

        contours = self.findContours(pred)
        self.__globalvm.imgModel.showContours(contours)

    def saveMask(self, win):
        delegate = ImageDelegate(self.__globalvm)
        f = delegate.selectSavePath(win)
        if f == "":
            return
        self.__globalvm.imgModel.saveMask(f)
