from argparse import ArgumentParser, ArgumentTypeError
from os.path import join, isdir, basename
from os import mkdir
from tifffile import imread, imwrite
from glob import glob
import yaml

from methods import MethodSelecter
from tools.time_decorator import Timer

METHODS_AVAILABLE = ["SD3D", "CP2.5D", "CP-SAM", "uSeg2.5D", "OP3D", "StitchCP2D", "StitchSD2D"]

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-m", "--method")
    parser.add_argument("-o", "--output")
    parser.add_argument("-v", "--verbose", type=str2bool, default=True)

    args = parser.parse_args()
    
    input_dir = args.input
    output_dir = args.output
    method_name = args.method

    verbose = args.verbose

    assert method_name in METHODS_AVAILABLE, f"{method_name} is an unknown method\nknown methods are {METHODS_AVAILABLE}"

    save_dir = join(output_dir, method_name)
    if not isdir(save_dir):
        mkdir(save_dir)

    name_no_dot = method_name.replace(".","")
    with open(join("methods_config",f"{name_no_dot}.yaml"), "r") as f_cfg:
        method_cfg = yaml.safe_load(f_cfg)

    if verbose: print(f"Setting up the --{method_name}-- model.")
    method = MethodSelecter(method_name, config = method_cfg)

    images_path = glob(join(input_dir, "*.tif"))


    for img_f in images_path:

        im_name = basename(img_f)
        if verbose: print(f"Processing image {im_name}")

        img = imread(img_f)

        with Timer("segment"):
            mask = method.segment(img)
        
        imwrite(join(save_dir, basename(img_f)), mask)

    with open(join(save_dir, "config.yaml"), "a") as f_cfg:
        yaml.dump(method_cfg, f_cfg, default_flow_style=False)

    with open(join(save_dir, "time.txt"), "a") as f_time:
        print(f"Mean time per file: {round(Timer.elapsed_time("segment"), 4)}s",file=f_time)


    
