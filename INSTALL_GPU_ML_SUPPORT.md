# Installation of keras with GPU support under Ubuntu 19.04

This document explains how I installed stuff to run tensorflow-ML models on my Nvidia 2080 card under Ubuntu 19.04.

For some parts, you can follow https://docs.nvidia.com/deeplearning/sdk/cudnn-install/, but I did not do it for everything.


# General setup of graphics card, CUDA, etc.

## NVidia graphics driver

Make sure to install the NVidia graphics driver for X.

## CUDA

Check whether CUDA is already installed, and what version:

    nvcc --version

If installed, it should output something like:

    nvcc --version
    nvcc: NVIDIA (R) Cuda compiler driver
    Copyright (c) 2005-2019 NVIDIA Corporation
    Built on Fri_Feb__8_19:08:17_PST_2019
    Cuda compilation tools, release 10.1, V10.1.105

In this case, I have CUDA 10.1. If you want that version under Ubuntu 19.04, all you have to do is:

   sudo apt install nvidia-cuda-toolkit

The only problem that remains is finding the CUDA installation afterwards. ;) It is in /usr/lib/cuda/.

    export CUDA_PATH=/usr/lib/cuda/

## CuDDN

Sadly, this requires an NVidia developer account, so you will have to create one. Then you can download it from here:


   https://developer.nvidia.com/rdp/cudnn-download


There was no release for Ubuntu 19.04 yet (only for the 18.04 LTS version), so I went for the general Linux version, called `cudnn-10.1-linux-x64-v7.6.2.24.tgz`.

    cd ~/Downloads/
    tar xzf cudnn-10.1-linux-x64-v7.6.2.24.tgz
    # the last command has created a dir named 'cuda' in your Downloads directory
    sudo cp cuda/include/cudnn.h ${CUDA_PATH}/include
    sudo cp cuda/lib64/libcudnn* ${CUDA_PATH}/lib64
    sudo chmod a+r ${CUDA_PATH}/include/cudnn.h ${CUDA_PATH}/lib64/libcudnn*


# Installation of tensorflow and keras via anaconda

source ~/software/anaconda3/etc/profile.d/conda.sh
conda create -y -n tensorflow-gpu python=3
conda activate tensorflow-gpu
conda install -y -c anaconda tensorflow-gpu
conda install -y keras


# Installation of tensorflow and keras via pip

No matter how hard I tried, this seems to be impossible due to a maze of version incompatibilities between cuda, cudaDNN, tensorflow, and ubuntu 19.04 (and ubuntu/docker/nvidia-docker when you try the docker way of installing tensorflow-gpu).


# Keras Backend configuration

There are multiple backends for Keras, tensorflow is only one of them. Follow instructions at https://keras.io/backend/ for details, but tensorflow should be default.

## Test that the tensorflow backend is used by Keras

    python -c "from keras import backend"

The output should include *Using TensorFlow backend*.


## Verify that the GPU can be used by tensorflow

    python -c 'import tensorflow as tf; tf.test.is_gpu_available()'


# Find the versions you have

## tensorflow-gpu: ```pip freeze | grep tensorflow-gpu```
## CUDA version: ```nvcc --version```
## cuDNN version: ```cat ${CUDA_PATH}/include/cudnn.h | grep CUDNN_MAJOR -A 2
