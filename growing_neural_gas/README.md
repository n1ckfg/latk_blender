# Growing Neural Gas Implementation

## Description
This is an implementation of Growing Neural Gas (GNG) algorithm, an unsupervised machine learning model based on Self-organizing Map (SOM) useful for learning topology of a data.
  
This method commonly used for data clustering, but there has been some interesting research to use GNG for performing 3D reconstruction task from raw point cloud data such as acquired from a 3D scanner or LIDAR. You can learn more in [here](https://ieeexplore.ieee.org/document/6889546).  

The GNG module I wrote in this repo is part of my bachelor thesis which concerned on 3D reconstruction for 3D scanned medical data, you can check out some of my results below (3D full head reconstruction). I don't have any plan soon to improve or maintain this GNG module, feel free to tinker with the module, some major improvement is to integrate 3D reconstruction code within the module.

## How to use the GNG module
The input data is an N-dimensional data in Numpy Array, with dimension ```[rows, cols, N]```
There are several hyperparameters you can adjust. To learn more, the [original GNG paper](https://papers.nips.cc/paper/893-a-growing-neural-gas-network-learns-topologies.pdf) explained pretty well about it. 
```
max_neurons # number of maximum neuron GNG can grow
max_iter # number of iteration to stop GNG grow
max_age # maximum age of edges connecting neurons
eb # fraction of distance betweeen nearest neuron and input signal
en # fraction of distance betweeen neighboring neurons and input signal
alpha # multiplying scalar for local error
beta # multiplying scalar for global error
```

## Example of use in 3D reconstruction
- Reconstructing a full human head (with iPhone X and [Standard Cyborg's app](https://www.standardcyborg.com/products)
![3D Head Image](https://github.com/rendchevi/growing-neural-gas/blob/master/assets/face_gng.png)
