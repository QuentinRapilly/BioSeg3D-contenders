import numpy as np
import matplotlib
matplotlib.rcParams["image.interpolation"] = 'none'

from glob import glob
from tqdm import tqdm
from tifffile import imread
from csbdeep.utils import Path, normalize
from tensorflow.config import list_physical_devices
import datetime as dt

from stardist import fill_label_holes, random_label_cmap, calculate_extents, gputools_available
from stardist import Rays_GoldenSpiral
#from stardist.matching import matching, matching_dataset
from stardist.models import Config3D, StarDist3D

import hydra
from omegaconf import DictConfig
from os.path import join


def random_fliprot(img, mask, axis=None): 
    if axis is None:
        axis = tuple(range(mask.ndim))
    axis = tuple(axis)
            
    assert img.ndim>=mask.ndim
    perm = tuple(np.random.permutation(axis))
    transpose_axis = np.arange(mask.ndim)
    for a, p in zip(axis, perm):
        transpose_axis[a] = p
    transpose_axis = tuple(transpose_axis)
    img = img.transpose(transpose_axis + tuple(range(mask.ndim, img.ndim))) 
    mask = mask.transpose(transpose_axis) 
    for ax in axis: 
        if np.random.rand() > 0.5:
            img = np.flip(img, axis=ax)
            mask = np.flip(mask, axis=ax)
    return img, mask 

def random_intensity_change(img):
    img = img*np.random.uniform(0.6,2) + np.random.uniform(-0.2,0.2)
    return img

def augmenter(x, y):
    """Augmentation of a single input/label image pair.
    x is an input image
    y is the corresponding ground-truth label image
    """
    # Note that we only use fliprots along axis=(1,2), i.e. the yx axis 
    # as 3D microscopy acquisitions are usually not axially symmetric
    x, y = random_fliprot(x, y, axis=(1,2))
    x = random_intensity_change(x)
    return x, y



@hydra.main(version_base=None, config_path="train_configs", config_name="SD3D")
def train(cfg : DictConfig):

    print(f"Gpu available : {list_physical_devices('GPU')}")

    train_images = sorted(glob(join(cfg["data"]["train"],"images/*.tif")))
    train_masks = sorted(glob(join(cfg["data"]["train"],"masks/*.tif")))

    X_trn = list(map(imread,train_images))
    Y_trn = list(map(imread,train_masks))

    axis_norm = (0,1,2)

    X_trn = [normalize(x,1,99.8,axis=axis_norm) for x in tqdm(X_trn)]
    Y_trn = [fill_label_holes(y) for y in tqdm(Y_trn)]

    n_channel = 1 if X_trn[0].ndim == 3 else X_trn[0].shape[-1]
    axis_norm = (0,1,2)   # normalize channels independently

    val_images = sorted(glob(join(cfg["data"]["val"],"images/*.tif")))
    val_masks = sorted(glob(join(cfg["data"]["val"],"masks/*.tif")))

    X_val = list(map(imread,val_images))
    Y_val = list(map(imread,val_masks))

    X_val = [normalize(x,1,99.8,axis=axis_norm) for x in tqdm(X_val)]
    Y_val = [fill_label_holes(y) for y in tqdm(Y_val)]


    n_rays = cfg["parameters"]["n_rays"]
    train_patch_size = tuple(cfg["parameters"]["train_patch_size"])
    train_batch_size = cfg["parameters"]["train_batch_size"]

    print(f"patch size : {train_patch_size}, type : {type(train_patch_size)}")

    # Use OpenCL-based computations for data generator during training (requires 'gputools')
    use_gpu = True and gputools_available()

    extents = calculate_extents(Y_trn)
    anisotropy = tuple(np.max(extents) / extents)

    # Predict on subsampled grid for increased efficiency and larger field of view
    grid = tuple(1 if a > 1.5 else 2 for a in anisotropy)

    # Use rays on a Fibonacci lattice adjusted for measured anisotropy of the training data
    rays = Rays_GoldenSpiral(n_rays, anisotropy=anisotropy)

    conf = Config3D (
        rays             = rays,
        grid             = grid,
        anisotropy       = anisotropy,
        use_gpu          = use_gpu,
        n_channel_in     = n_channel,
        # adjust for your data below (make patch size as large as possible)
        train_patch_size = train_patch_size,
        train_batch_size = train_batch_size,
    )

    if use_gpu:
        from csbdeep.utils.tf import limit_gpu_memory
        # adjust as necessary: limit GPU memory to be used by TensorFlow to leave some to OpenCL-based computations
        limit_gpu_memory(fraction = 0.8, total_memory = cfg["gpu"]["memory"])


    model = StarDist3D(conf, name=cfg["save"]["name"]+f"_{str(dt.datetime.now()).replace(' ','_').split('.')[0]}",
                       basedir=cfg["save"]["path"])


    model.train(X_trn, Y_trn, validation_data=(X_val,Y_val),
                epochs= cfg["parameters"]["nb_epochs"], augmenter=augmenter)


    model.optimize_thresholds(X_val, Y_val)

if __name__ == "__main__":
    train()