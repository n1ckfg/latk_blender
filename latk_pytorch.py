import numpy as np
import cv2

import torch
from torch.autograd import Variable
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision import datasets
import itertools

import bpy

from . import latk_ml 

from . vox2vox.models import *
from . vox2vox.dataset import CTDataset

from . informative_drawings.model import Generator 

from . pix2pix.models import pix2pix_model

def getPyTorchDevice(mps=True):
    device = None
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available() and mps==True:
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    return device

def createPyTorchNetwork(name, modelPath, net_G, device): #, input_nc=3, output_nc=1, n_blocks=3):
    #device = getPyTorchDevice()
    modelPath = latk_ml.getModelPath(name, modelPath)
    net_G.to(device)
    net_G.load_state_dict(torch.load(modelPath, map_location=device))
    net_G.eval()
    return net_G


class Informative_Drawings_PyTorch():
    def __init__(self, name, modelPath):
        self.device = getPyTorchDevice()         
        generator = Generator(3, 1, 3) # input_nc=3, output_nc=1, n_blocks=3
        self.net_G = createPyTorchNetwork(name, modelPath, generator, self.device)   

    def detect(self, srcimg):
        with torch.no_grad():   
            srcimg2 = np.transpose(srcimg, (2, 0, 1))

            tensor_array = torch.from_numpy(srcimg2)
            input_tensor = tensor_array.to(self.device)
            output_tensor = self.net_G(input_tensor)

            result = output_tensor.detach().cpu().numpy().transpose(1, 2, 0)
            result *= 255
            result = cv2.resize(result, (srcimg.shape[1], srcimg.shape[0]))
            
            return result


class Pix2Pix_PyTorch():
    def __init__(self, name, modelPath):
        self.device = getPyTorchDevice() 
        
        Opt = namedtuple("Opt", ["model","gpu_ids","isTrain","checkpoints_dir","name","preprocess","input_nc","output_nc","ngf","netG","norm","no_dropout","init_type", "init_gain","load_iter","dataset_mode","epoch"])
        opt = Opt("pix2pix", [], False, "", "", False, 3, 3, 64, "unet_256", "batch", True, "normal", 0.02, 0, "aligned", "latest")

        generator = pix2pix_model.Pix2PixModel(opt).netG 

        self.net_G = createPyTorchNetwork(name, modelPath, generator, self.device)   

    def detect(self, srcimg):
        with torch.no_grad():  
            srcimg2 = cv2.resize(srcimg, (256, 256))
            input_image = cv2.cvtColor(srcimg2, cv2.COLOR_BGR2RGB)
            input_image = input_image.transpose(2, 0, 1)
            input_image = np.expand_dims(input_image, axis=0)
            #input_image = input_image / 255.0
            input_image = (input_image - 0.5) / 0.5 
            input_image = input_image.astype('float32')

            tensor_array = torch.from_numpy(input_image)
            input_tensor = tensor_array.to(self.device)
            output_tensor = self.net_G(input_tensor)

            result = output_tensor[0].detach().cpu().numpy() #.transpose(1, 2, 0)
            result = np.clip(((result*0.5+0.5) * 255), 0, 255) #.astype(np.uint8) 
            result = result.transpose(1, 2, 0) #.astype('uint8')
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

            #result = output_tensor.detach().cpu().numpy().transpose(1, 2, 0)
            #result *= 255
            
            result = cv2.resize(result, (srcimg.shape[1], srcimg.shape[0]))
            
            return result


class Vox2Vox_PyTorch():
    def __init__(self, name, modelPath):
        self.device = getPyTorchDevice(mps=False) # MPS needs to support operator aten::slow_conv3d_forward          
        generator = GeneratorUNet()
        if self.device.type == "cuda":
            generator = generator.cuda()

        self.net_G = createPyTorchNetwork(name, modelPath, generator, self.device)

        self.transforms_ = transforms.Compose([
            transforms.ToTensor()
        ])

    def detect(self):
        Tensor = None
        if self.device.type == "cuda":
            Tensor = torch.cuda.FloatTensor
        else:
            Tensor = torch.FloatTensor

        val_dataloader = DataLoader(
            CTDataset(bpy.app.tempdir, transforms_=self.transforms_, isTest=True),
            batch_size=1,
            shuffle=False,
            num_workers=0,
        )

        dataiter = iter(val_dataloader)
        imgs = next(dataiter) #dataiter.next()

        """Saves a generated sample from the validation set"""
        real_A = Variable(imgs["A"].unsqueeze_(1).type(Tensor))
        #real_B = Variable(imgs["B"].unsqueeze_(1).type(Tensor))
        fake_B = self.net_G(real_A)

        return fake_B.cpu().detach().numpy()