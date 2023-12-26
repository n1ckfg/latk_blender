import numpy as np
import cv2
import onnxruntime as ort
import bpy
from . import latk_ml

def createOnnxNetwork(name, modelPath):
    modelPath = latk_ml.getModelPath(name, modelPath)
    net = None

    so = ort.SessionOptions()
    so.log_severity_level = 3
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL    
    so.enable_mem_pattern = True
    so.enable_cpu_mem_arena = True
    
    #if (ort.get_device().lower() == "gpu"):
    net = ort.InferenceSession(modelPath, so, providers=["CUDAExecutionProvider", "CoreMLExecutionProvider", "CPUExecutionProvider"])
    #else:
        #net = ort.InferenceSession(modelPath, so)

    return net


class Informative_Drawings_Onnx():
    def __init__(self, name, modelPath):       
        self.net = createOnnxNetwork(name, modelPath)
        
        input_shape = self.net.get_inputs()[0].shape
        self.input_height = int(input_shape[2])
        self.input_width = int(input_shape[3])
        self.input_name = self.net.get_inputs()[0].name
        self.output_name = self.net.get_outputs()[0].name

    def detect(self, srcimg):
        img = cv2.resize(srcimg, dsize=(self.input_width, self.input_height))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        blob = np.expand_dims(np.transpose(img.astype(np.float32), (2, 0, 1)), axis=0).astype(np.float32)
        outs = self.net.run([self.output_name], {self.input_name: blob})

        result = outs[0].squeeze()
        result *= 255
        result = cv2.resize(result.astype('uint8'), (srcimg.shape[1], srcimg.shape[0]))
        return result


# https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/issues/1113
class Pix2Pix_Onnx():
    def __init__(self, name, modelPath):
        self.net = createOnnxNetwork(name, modelPath)

        self.input_size = 256
        self.input_name = self.net.get_inputs()[0].name
        self.output_name = self.net.get_outputs()[0].name
        print("input_name = " + self.input_name)
        print("output_name = " + self.output_name)

    def detect(self, srcimg):
        if isinstance(srcimg, str):
            srcimg=cv2.imdecode(np.fromfile(srcimg, dtype=np.uint8), -1)
        elif isinstance(srcimg, np.ndarray):
            srcimg=srcimg.copy()
        # srcimg=srcimg[0:256, 0:256]
        img = cv2.resize(srcimg, (self.input_size, self.input_size))
        input_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        input_image = input_image.transpose(2, 0, 1)
        input_image = np.expand_dims(input_image, axis=0)
        #input_image = input_image / 255.0
        input_image = (input_image - 0.5) / 0.5 
        input_image = input_image.astype('float32')
        print(input_image.shape)
        # x = x[None,:,:,:]
        outs = self.net.run(None, {self.input_name: input_image})[0].squeeze(axis=0)
        outs = np.clip(((outs*0.5+0.5) * 255), 0, 255).astype(np.uint8) 
        outs = outs.transpose(1, 2, 0).astype('uint8')
        outs = cv2.cvtColor(outs, cv2.COLOR_RGB2BGR)
        outs = np.hstack((img, outs))
        print("outs",outs.shape)
        
        # [y:y+height, x:x+width]
        outs = outs[0:256, 256:512]
        return cv2.resize(outs, (srcimg.shape[1], srcimg.shape[0]))
