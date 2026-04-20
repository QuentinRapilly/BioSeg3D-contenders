# Package installation guideline

We advise users to create one virtual environments per method available in this repository to avoid package conflict.

```bash
python -m venv <env_name>
source <env_name>/bin/activate
```

In each environment, we advise to use `uv` instead of `pip` for package management as it is generally much faster and better at solving complicated dependencies.

```bash
pip install uv
```

For each of the following packages we consider that you have created a clean environment with `uv`.

For all methods, modules `csbdeep` and `pyyaml` are mandatory so install them with:

```bash
uv pip install csbdeep
uv pip install pyyaml
```

## Cellpose (<4.0.0, i.e. not Cellpose SAM) and CellStitch

**This environment can be used to run both CP2.5D and StitchCP2D.**

/!\ Cellstitch requires Cellpose but is not compatible with Cellpose-SAM

The following line install Torch working with GPU (Cuda + CudNN):

```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

You can then add Cellpose with:

```bash
uv pip install cellpose==3.1.0
```

You can pick an earlier Cellpose version but the 3.1 brings updated tools for 2.5D segmentation so we advise keeping this one.

### Adding CellStitch

The CellStitch package cannot be downloaded with `uv/pip` directly, you have to download it before. Clone it with:

```bash
git clone https://github.com/imyiningliu/cellstitch.git
```

The URL of the git being [https://github.com/imyiningliu/cellstitch/](https://github.com/imyiningliu/cellstitch/).

Once the files are dowloaded, you will have to modify some lines:

#### Change 1

To prevent the module to stitch two objects with 0 IoU, change file `alignement.py` line 119, from:

```python
if lbl0 != 0 and stitch_cell:
```

to

```python
if lbl0 != 0 and stitch_cell and filtered_C[lbl0_index]<1:
```

#### Change 2

`numpy.Inf` is no longer supported by `numpy>=2.0.0`, and has been replaced by `np.inf`. So change all the lines where `numpy.Inf` is used (file `alignement.py` line 111 and 155).

#### Installation

Once the two changes are done, you can install the package with:

```bash
cd cellstitch
uv pip install -e .
```

## Cellpose-SAM

**This environment can be used to run CP-SAM.**

The following line install Torch working with GPU (Cuda + CudNN):

```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

You can then add Cellpose-SAM with:

```bash
uv pip install cellpose==4.1.0
```

Or any new version of Cellpose-SAM that does not bring to many changes making the code of this repo unusable.

## uSegment3D

**This environment can be used to run uSeg2.5D.**

The following line install Torch working with GPU (Cuda + CudNN):

```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

You can then add uSegment3D with:

```bash
uv pip install u-Segment3D
```

## Omnipose

**This environment can be used to run OP3D.**

The following line install Torch working with GPU (Cuda + CudNN):

```bash
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

### Adding Omnipose - Method 1

On the cluster that I use, the latest python version is 3.10 which is uncompatible with the latest version of Omnipose released in Jan 2026.

But if your Python is compatible (i.e., `python>=3.11`), consider just adding omnipose with:

```bash
uv pip install omnipose
```

### Adding Omnipose - Method 2

If your python version is not compatible, consider using the version 1.0.6.

```bash
uv pip install omnipose==1.0.6
```

Add package `natsort` which is not included by default.

```bash
uv pip install natsort
```

Then when you run the command

```bash
python launch-seg.py -i <input dir> -o <output dir> -m OP3D
```

You may encounter the error:

```bash
ImportError: cannot import name 'ifft' from 'scipy'
```

This error occur because methods `fft` and `ifft` called by package `peakdetect` are no longer in `scipy` but in `scipy.fft` so locate the file that makes the import inside the error message (something like `<location of your virtual env>/lib/python3.9/site-packages/peakdetect/peakdetect.py`), and modify the corresponding lines:

```bash
nano <location of your virtual env>/lib/python3.9/site-packages/peakdetect/peakdetect.py
```

And change the line 3 from:

```python
from scipy import fft, ifft
```

to

```python
from scipy.fft import fft, ifft
```

This fix worked for me, if the 1.0.6 package is no longer available via pip, consider following the procedure depicted below.

### Adding Omnipose - Method 3

- Downloading version tag 1.0.6 on the git [https://github.com/kevinjohncutler/omnipose/releases/tag/v1.0.6](https://github.com/kevinjohncutler/omnipose/releases/tag/v1.0.6).

- Unzip the archive.

- Rename and enter the directory: `mv omnipose-1.0.6 omnipose && cd omnipose`

- One cannot install a dev version of a package without specifying the version tag. So run `export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OMNIPOSE=1.0.6`

- Install the package with `uv pip install -e .`

Once all those steps are done, the package should be installed correctly but a dependency may remain incorrect. If when you run the code you encounter the error:

Go back to method 2 and follow the instruction starting by the one to install `natsort`.

### Training using RAdam

If you consider training Omnipose with optimizer RAdam, you should also install it:

```bash
uv pip install pytorch-optimizer
```

## StarDist 2D/3D + Cellstitch

**This environment can be used to run both SD3D and StitchSD2D.**

The following line install TensorFlow working with GPU (Cuda + CudNN):

```bash
uv pip install tensorflow[and-cuda]==2.14.0
```

/!\ You can consider installing an other version but make sur it is compatible with Stardist + you GPU + Cuda + CudNN.

```bash
uv pip install stardist
```

If errors appear, it might be because you should downgrade `numpy` to a version earlier than 2.0.

You can do it with:

```bash
uv pip install numpy==1.26.1
```

### Adding Cellstitch

Follow the instructions provided in the Cellpose Section but before the **Installation** step add another change:

#### Change 3

In the file `requirements.txt` change the line concerning Cellpose from:

`cellpose >= 2.0.4` to `cellpose == 3.1.0`
