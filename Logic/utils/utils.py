# -*- coding: utf-8 -*-
# Author: Xiangde Luo
# Date:   2 Sep., 2021
# Implementation of MIDeepSeg for interactive medical image segmentation and annotation.
# Reference:
#     X. Luo and G. Wang et al. MIDeepSeg: Minimally interactive segmentation of unseen objects
#     from medical images using deep learning. Medical Image Analysis, 2021. DOI:https://doi.org/10.1016/j.media.2021.102102.

'''
为了尽可能的统一本工程的命名规则，这个文件直接拷贝自https://github.com/HiLab-git/MIDeepSeg
'''
import GeodisTK
import numpy as np
from PySide6 import QtGui
from PySide6.QtGui import QImage
from scipy import ndimage

def cropped_image(image, bbox, pixel=0):
    random_bbox = [bbox[0] - pixel, bbox[1] -
                   pixel, bbox[2] + pixel, bbox[3] + pixel]
    cropped = image[random_bbox[0]:random_bbox[2],
                    random_bbox[1]:random_bbox[3]]
    return cropped
def extends_points(seed):
    if (seed.sum() > 0):
        points = ndimage.distance_transform_edt(seed == 0)
        points[points > 2] = 0
        points[points > 0] = 1
    else:
        points = seed
    return points.astype(np.uint8)


def QImageToCvMat(incomingImage):
    '''
    Converts a QImage into an opencv MAT format
    from https://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
    '''

    incomingImage = incomingImage.convertToFormat(QtGui.QImage.Format.Format_RGB32)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.constBits()
    arr = np.array(ptr).reshape(height, width, 4)  # Copies the data
    return arr


def QImageToGrayCvMat(incomingImage):
    '''
    Converts a QImage into an opencv MAT format
    from https://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
    '''

    incomingImage = incomingImage.convertToFormat(QtGui.QImage.Format.Format_Grayscale8)

    width = incomingImage.width()
    height = incomingImage.height()

    ptr = incomingImage.constBits()
    arr = np.array(ptr).reshape(height, width)  # Copies the data
    return arr




def itensity_normalization(image):
    out = (image - image.min()) / (image.max() - image.min())
    out = out.astype(np.float32)
    return out


def cstm_normalize(im, max_value=1.0):
    """
    Normalize image to range 0 - max_value
    """
    imn = max_value * (im - im.min()) / max((im.max() - im.min()), 1e-8)
    return imn


def interaction_geodesic_distance(img, seed, threshold=0):
    if seed.sum() > 0:
        # I = itensity_normalize_one_volume(img)
        I = np.asanyarray(img, np.float32)
        S = seed
        geo_dis = GeodisTK.geodesic2d_fast_marching(I, S)
        # geo_dis = GeodisTK.geodesic2d_raster_scan(I, S, 1.0, 2.0)
        if threshold > 0:
            geo_dis[geo_dis > threshold] = threshold
            geo_dis = geo_dis / threshold
        else:
            geo_dis = np.exp(-geo_dis)
    else:
        geo_dis = np.zeros_like(img, dtype=np.float32)
    return cstm_normalize(geo_dis)


def zoom_image(data, outputsize=(96, 96)):
    """
    reshape image to 64*64 pixels
    """
    x, y = data.shape
    zoomed_image = ndimage.zoom(data, (outputsize[0] / x, outputsize[0] / y))
    return zoomed_image

def itensity_standardization(image):
    """
    normalize the itensity of an nd volume based on the mean and std of nonzeor region
    inputs:
        volume: the input nd volume
    outputs:
        out: the normalized nd volume
    """
    pixels = image[image > 0]
    mean = pixels.mean()
    std = pixels.std()
    out = (image - mean)/std
    out = out.astype(np.float32)
    return out

def interaction_refined_geodesic_distance(img, seed, threshold=0):
    if seed.sum() > 0:
        # I = itensity_normalize_one_volume(img)
        I = np.asanyarray(img, np.float32)
        S = seed
        geo_dis = GeodisTK.geodesic2d_fast_marching(I, S)
        if threshold > 0:
            geo_dis[geo_dis > threshold] = threshold
            geo_dis = geo_dis / threshold
        else:
            geo_dis = np.exp(-geo_dis**2)
    else:
        geo_dis = np.zeros_like(img, dtype=np.float32)
    return geo_dis