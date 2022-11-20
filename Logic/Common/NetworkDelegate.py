import numpy as np
import torch.cuda

from Logic.Common.network import UNet
from Logic.utils.Pathdb import get_resource_path


class NetworkDelegate:
    __model: UNet
    __cuda: bool

    def __init__(self, cuda: bool, model):
        self.__cuda = cuda
        self.__model = self.device_wrapper(model)

    def device_wrapper(self, input):
        return input.cuda() if self.__cuda else input.cpu()

    def loadModel(self, pth):
        if self.__cuda:
            self.__model.load_state_dict(pth)
        else:
            self.__model.load_state_dict(torch.load(pth, map_location="cpu"))
        self.__model.eval()

    @torch.no_grad()
    def inference(self, input) -> np.ndarray:
        input = self.device_wrapper(torch.from_numpy(input))
        out = self.__model(input).squeeze(0)
        out = torch.softmax(out, dim=0).cpu().numpy()
        # 网络输出的是[bg,fg]转化[fg,bg]
        out[0, 1] = out[1, 0]
        return out


if __name__ == '__main__':
    delete = NetworkDelegate(False, UNet(2, 2, 16))
    delete.loadModel(get_resource_path("Res/iter_15000.pth"))
    fg, bk = delete.inference(delete.device_wrapper(torch.randn((1, 2, 96, 96))))
    print(fg.shape)
    print(bk.shape)
