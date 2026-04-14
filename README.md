# BioSeg3D Contenders

This repository was created during the writing of the journal paper for [Nagini3D](https://github.com/QuentinRapilly/NAGINI-3D/) to facilitate the setup of experiments by unifying the code for running concurrent methods.

The implemented methods are:

- Stardist 3D (referred to as SD3D);
- Omnipose 3D (OP3D);
- Cellpose-SAM (CP-SAM), a version of Cellpose using a SAM-style transformer with Cellpose's own 3D aggregation method;
- Cellpose 2.5D (CP2.5D), Cellpose's own 3D aggregation method, pre CP-SAM version;
- Cellstitch + Stardist 2D (StitchSD2D);
- Cellstitch + Cellpose 2D (StitchCP2D).

## Virtual envs

To use this repository, it is essential to have initialized virtual environments containing the packages required for the various methods.

TODO: donner des détails de comment faire.

## Configuration files

In the "methods_config" folder, there is a configuration file for each method. This is where you should modify the hyperparameters for each method.

## Segmentation

To launch the segmentation using a specific method, run the following command line in a environment with the appropriate modules for that method (see Virtual ens):
`python launch_seg.py -i <dir to input images> -o <dir to the storage of results> -m <method name>`

Method name should one of: SD3D, OP3D, CP2.5D, CP-SAM, uSeg2.5D, StitchCP2D, StitchSD2D.
