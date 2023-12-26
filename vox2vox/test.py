import argparse
import os
import numpy as np
import math
import itertools
import time
import datetime
import sys

import torchvision.transforms as transforms
from torchvision.utils import save_image

from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

from models import *
from dataset import CTDataset

from dice_loss import diceloss

import torch.nn as nn
import torch.nn.functional as F
import torch

import h5py
import binvox_rw

def test():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch", type=int, default=200, help="epoch to start training from")
    parser.add_argument("--n_epochs", type=int, default=200, help="number of epochs of training")
    parser.add_argument("--dataset_name", type=str, default="leftkidney_3d", help="name of the dataset")
    parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
    parser.add_argument("--glr", type=float, default=0.0002, help="adam: generator learning rate")
    parser.add_argument("--dlr", type=float, default=0.0002, help="adam: discriminator learning rate")
    parser.add_argument("--b1", type=float, default=0.5, help="adam: decay of first order momentum of gradient")
    parser.add_argument("--b2", type=float, default=0.999, help="adam: decay of first order momentum of gradient")
    parser.add_argument("--decay_epoch", type=int, default=100, help="epoch from which to start lr decay")
    parser.add_argument("--n_cpu", type=int, default=8, help="number of cpu threads to use during batch generation") #8
    parser.add_argument("--img_height", type=int, default=128, help="size of image height")
    parser.add_argument("--img_width", type=int, default=128, help="size of image width")
    parser.add_argument("--img_depth", type=int, default=128, help="size of image depth")
    parser.add_argument("--channels", type=int, default=1, help="number of image channels")
    parser.add_argument("--disc_update", type=int, default=5, help="only update discriminator every n iter")
    parser.add_argument("--d_threshold", type=int, default=.8, help="discriminator threshold")
    parser.add_argument("--threshold", type=int, default=-1, help="threshold during sampling, -1: No thresholding")
    parser.add_argument("--sample_interval", type=int, default=1, help="interval between sampling of images from generators")
    parser.add_argument("--checkpoint_interval", type=int, default=50, help="interval between model checkpoints") #-1
    opt = parser.parse_args()
    print(opt)

    #os.makedirs("output/%s" % opt.dataset_name, exist_ok=True)
    #os.makedirs("saved_models/%s" % opt.dataset_name, exist_ok=True)

    cuda = True if torch.cuda.is_available() else False

    # Loss functions
    criterion_GAN = torch.nn.MSELoss()
    criterion_voxelwise = diceloss()

    # Loss weight of L1 voxel-wise loss between translated image and real image
    lambda_voxel = 100

    # Calculate output of image discriminator (PatchGAN)
    patch = (1, opt.img_height // 2 ** 4, opt.img_width // 2 ** 4, opt.img_depth // 2 ** 4)

    # Initialize generator and discriminator
    generator = GeneratorUNet()
    discriminator = Discriminator()

    if cuda:
        generator = generator.cuda()
        discriminator = discriminator.cuda()
        criterion_GAN.cuda()
        criterion_voxelwise.cuda()

    #if opt.epoch != 0:
        # Load pretrained models
    #generator.load_state_dict(torch.load("saved_models/%s/generator_%d.pth" % (opt.dataset_name, opt.epoch)))
    #discriminator.load_state_dict(torch.load("saved_models/%s/discriminator_%d.pth" % (opt.dataset_name, opt.epoch)))
    generator.load_state_dict(torch.load("model/generator_" + str(opt.epoch) + ".pth"))
    discriminator.load_state_dict(torch.load("model/discriminator_" + str(opt.epoch) + ".pth"))
    #else:
        # Initialize weights
        #generator.apply(weights_init_normal)
        #discriminator.apply(weights_init_normal)

    # Optimizers
    optimizer_G = torch.optim.Adam(generator.parameters(), lr=opt.glr, betas=(opt.b1, opt.b2))
    optimizer_D = torch.optim.Adam(discriminator.parameters(), lr=opt.dlr, betas=(opt.b1, opt.b2))

    # Configure dataloaders
    transforms_ = transforms.Compose([
        # transforms.Resize((opt.img_height, opt.img_width, opt.img_depth), Image.BICUBIC),
        transforms.ToTensor(),
        # transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    '''
    dataloader = DataLoader(
        CTDataset("../../data/%s/train/" % opt.dataset_name, transforms_=transforms_),
        batch_size=opt.batch_size,
        shuffle=True,
        num_workers=opt.n_cpu,
    )
    '''

    val_dataloader = DataLoader(
        CTDataset("input/", transforms_=transforms_, isTest=True),
        batch_size=1,
        shuffle=False,
        num_workers=0,
    )

    # Tensor type
    Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor

    def write_binvox(data, path):
        data = np.rint(data).astype(np.uint8)
        dims = (opt.img_width, opt.img_height, opt.img_depth) #data.shape
        translate = [0, 0, 0]
        scale = 1.0
        axis_order = 'xzy'
        v = binvox_rw.Voxels(data, dims, translate, scale, axis_order)

        with open(path, 'bw') as f:
            v.write(f)

    dataiter = iter(val_dataloader)

    def sample_voxel_volumes(index):
        imgs = next(dataiter) #dataiter.next()

        """Saves a generated sample from the validation set"""
        real_A = Variable(imgs["A"].unsqueeze_(1).type(Tensor))
        #real_B = Variable(imgs["B"].unsqueeze_(1).type(Tensor))
        fake_B = generator(real_A)

        # convert to numpy arrays
        real_A = real_A.cpu().detach().numpy()
        #real_B = real_B.cpu().detach().numpy()
        fake_B = fake_B.cpu().detach().numpy()

        image_folder = "output" #/%s_%s_" % (opt.dataset_name, index)

        #write_binvox(real_A, image_folder + 'real_A.binvox')

        write_binvox(fake_B, os.path.join(image_folder, os.path.basename(imgs["url"][0]) + "_fake.binvox"))

    for i, batch in enumerate(val_dataloader):
      sample_voxel_volumes(i)
      print('*****volume ' + str(i+1) + '/' + str(len(val_dataloader)) + ' sampled*****')


if __name__ == '__main__':
    dataiter = None

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    test()
