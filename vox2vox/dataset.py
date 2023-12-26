from torch.utils.data import Dataset, DataLoader
import h5py
import numpy as np
import glob

class CTDataset(Dataset):
    def __init__(self, datapath, transforms_, isTest=False):
        self.datapath = datapath
        self.transforms = transforms_
        self.isTest = isTest
        #self.samples = ['../..'+x.split('.')[4] for x in glob.glob(self.datapath + '/*.im')]
        self.samples = [x.split('.')[0] for x in glob.glob(self.datapath + '/*.im')]
        if (self.isTest == True):
        	self.samples.sort()

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        image = h5py.File(self.samples[idx] + '.im', 'r').get('data')[()]
        
        if (self.isTest == False):
            mask = h5py.File(self.samples[idx] + '.seg', 'r').get('data')[()]
            
            if self.transforms:
                image, mask = self.transforms(image), self.transforms(mask)
            
            return { "A": image, "B": mask }
        else:
            if self.transforms:
                image = self.transforms(image)
            
            return { "A": image, "B": image, "url": self.samples[idx] }            
