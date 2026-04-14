from argparse import ArgumentParser
from os.path import join, isdir, basename
from os import mkdir
from tifffile import imread, imwrite
from glob import glob
import yaml

from methods import MethodSelecter
from time_decorator import Timer


METHODS_AVAILABLE = ["SD3D", "CP2.5D", "CP-SAM", "uSeg2.5D", "OP3D", "StitchCP2D", "StitchSD2D"]

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-m", "--method")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()
    
    input_dir = args.input
    output_dir = args.output
    method_name = args.method

    assert method_name in METHODS_AVAILABLE, "Unknown method"

    save_dir = join(output_dir, method_name)
    if not isdir(save_dir):
        mkdir(save_dir)

    with open(join("methods_config",f"{method_name.replace(".","")}.yaml"), "r") as f_cfg:
        method_cfg = yaml.safe_load(f_cfg)

    method = MethodSelecter(method_name, config = method_cfg)

    images_path = glob(join(input_dir, "*.tif"))


    for img_f in images_path:
        img = imread(img_f)

        with Timer():
            mask = method.segment()
        
        imwrite(join(save_dir, basename(img_f)), mask)

    with open(join(save_dir, "time.txt"), "a") as f_time:
        print(f"Mean time per file: {round(Timer.elapsed_time(), 4)}",file=f_time)


    
