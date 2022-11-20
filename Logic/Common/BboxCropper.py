import numpy as np


class BboxCropper:
    bbox: list
    __img_shape: tuple

    def __init__(self, seed, img_shape):
        '''
        # 根据seed最左、上、右、下四个点 (生成bbox，创建裁剪器)
        :param seed:
        '''
        self.__img_shape = img_shape
        self.bbox = self.get_start_end_points(seed, img_shape)

    def get_start_end_points(self, scribbles, shape):
        points = np.where(scribbles != 0)
        minZidx = int(np.min(points[0]))
        maxZidx = int(np.max(points[0]))
        minXidx = int(np.min(points[1]))
        maxXidx = int(np.max(points[1]))
        start_end_points = [minZidx - 5, minXidx - 5, maxZidx + 5, maxXidx + 5]
        if start_end_points[0] < 0:
            start_end_points[0] = 0

        if start_end_points[2] > shape[0]:
            start_end_points[2] = shape[0]

        if start_end_points[1] < 0:
            start_end_points[1] = 0

        if start_end_points[3] > shape[1]:
            start_end_points[3] = shape[1]
        return start_end_points

    def crop1d(self, image, pixel=0):
        random_bbox = [self.bbox[0] - pixel, self.bbox[1] -
                       pixel, self.bbox[2] + pixel, self.bbox[3] + pixel]
        cropped = image[random_bbox[0]:random_bbox[2],
                  random_bbox[1]:random_bbox[3]]
        return np.array(cropped)

    def crop2d(self, image, pixel=0):
        random_bbox = [self.bbox[0] - pixel, self.bbox[1] -
                       pixel, self.bbox[2] + pixel, self.bbox[3] + pixel]
        cropped = image[:, random_bbox[0]:random_bbox[2],
                  random_bbox[1]:random_bbox[3]]
        return np.array(cropped)

    def getBbox(self):
        return self.bbox
