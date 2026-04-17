from csbdeep.utils import normalize
import numpy as np

from tools.cellstitch_aux import apply_model, post_process

class MethodSelecter:

    def __init__(self, method_name, config):

        self.method_name = method_name

        self.config = config

        assert method_name in ["SD3D", "CP2.5D", "CP-SAM", "uSeg2.5D", "OP3D",
                               "StitchCP2D", "StitchSD2D"], "Unknown method"

        if method_name == "SD3D":
            from stardist.models import StarDist3D
            from tensorflow.config import list_physical_devices
            #config = {"use_gpu": (len(list_physical_devices("GPU"))>0)}
            self.model = StarDist3D(None,
                                    name=config["model_name"],
                                    basedir=config["models_dir"])
        
        if method_name == "CP2.5D":
            from cellpose.models import CellposeModel
            from torch.cuda import is_available
            use_gpu = is_available()
            self.model = CellposeModel(model_type=self.config["model_name"],
                                       gpu=use_gpu)
            self.parameters = self.config["model_parameters"] # mettre dans la config {"batch_size" : 128, "diameter" : 15, "channels" : [0,0], "do_3D" : True, "dP_smooth" : 3}

        if method_name == "CP-SAM":
            from cellpose import models, core, io
            if core.use_gpu()==False:
                raise ImportError("No GPU access, change your runtime")

            self.model = models.CellposeModel(gpu=True)

        if method_name == "uSeg2.5D":
            import segment3D.parameters as uSegment3D_params
            
            from torch.cuda import is_available

            import segment3D.usegment3d as uSegment3D
            import segment3D.file_io as uSegment3D_fio
            import scipy.ndimage as ndimage
            self.useg = uSegment3D
            self.usef_fio = uSegment3D_fio
            self.ndimage = ndimage

            self.pad_size = 0

            preprocess_params = uSegment3D_params.get_preprocess_params()
            self.preprocess_params = self.config["preprocess_params"] | preprocess_params

            cellpose_params = uSegment3D_params.get_Cellpose_autotune_params()
            self.cellpose_params = self.config["cellpose_params"] | cellpose_params\
                | {"histnorm_kernel_size": (512, 512), "diam_range": np.arange(2,50,2),
                   "gpu": is_available()}

        
            aggreg_params = uSegment3D_params.get_2D_to_3D_aggregation_params()
            self.aggreg_params = self.config["aggreg_params"] | aggreg_params


        if method_name == "OP3D":
            from cellpose_omni import models, core
            use_GPU = core.use_gpu()
            self.model = models.CellposeModel(gpu=use_GPU, net_avg=False, **self.config["model"])

            self.parameters = config["parameters"]

        if method_name == "StitchCP2D":
            from cellstitch.pipeline import full_stitch
            self.stitch = full_stitch
            from torch.cuda import is_available
            from cellpose.models import Cellpose
            use_gpu = is_available()
            self.model = Cellpose(model_type=self.config["model_name"],
                                  gpu=use_gpu)
            self.parameters = self.config["model_parameters"] # {"diameter" : 10, "channels" : [0,0], "flow_threshold" : 1.0, "batch_size" : 128}
            self.d = self.config["main_direction"]

        if method_name == "StitchSD2D":
            from cellstitch.pipeline import full_stitch
            self.stitch = full_stitch
            from stardist.models import StarDist2D
            self.model = StarDist2D.from_pretrained("2D_versatile_fluo")
            self.parameters = {}
            self.d = self.config["main_direction"]


    def segment(self, image):
        axis_norm = (0,1,2) 
        img_norm = normalize(image, 1,99.8, axis=axis_norm)

        if self.method_name == "SD3D":  
            #n_channel = 1 if image.ndim == 3 else image.shape[-1]
            labels, _ = self.model.predict_instances(img_norm)
            return labels

        if self.method_name == "CP2.5D":
            res = self.model.eval(img_norm, **self.parameters, z_axis=0, progress=True)[0]
            return res
        
        if self.method_name == "CP-SAM":
            mask, _, _ = self.model.eval(img_norm[...,None], **self.config)
            return mask
        
        if self.method_name == "OP3D":
            mask, _, _ = self.model.eval(img_norm, niter=10, **self.parameters)
            return mask
        
        if self.method_name in ["StitchCP2D", "StitchSD2D"]:
            xy_masks = apply_model(self.model, self.method_name,
                                   img_norm, self.parameters)
            yz_masks = apply_model(self.model, self.method_name,
                                   img_norm.transpose(1,0,2),
                                   self.parameters).transpose(1,0,2)
            xz_masks = apply_model(self.model, self.method_name,
                                   img_norm.transpose(2,1,0),
                                   self.parameters).transpose(2,1,0)
            
            masks = [xy_masks, yz_masks, xz_masks]
            d = self.d
            mask = self.stitch(masks[d], masks[(d+1)%3], masks[(d+2)%3])
            return post_process(mask)
        
        if self.method_name == "uSeg2.5D":
            pad_size = self.pad_size
            img = np.pad(img_norm, [[pad_size, pad_size], [pad_size, pad_size], [pad_size, pad_size]], mode='constant')
            img[img==0] = np.nanmedian(img[img>0])
            img = self.ndimage.median_filter(img, size=3)

            img_preprocess = self.useg.preprocess_imgs(img, params=self.preprocess_params)
            img_preprocess = np.squeeze(img_preprocess)[...,None]

            if len(img_preprocess.shape) ==3: # 3D volume 
                img_preprocess = img_preprocess[...,None] # we generate an artificial channel
            
            _, img_segment_3D_xy_probs, img_segment_2D_xy_flows, _ = self.useg.Cellpose2D_model_auto(
                img_preprocess, view='xy', params=self.cellpose_params, basename=None, savefolder=None)
            _, img_segment_3D_xz_probs, img_segment_2D_xz_flows, _ = self.useg.Cellpose2D_model_auto(
                img_preprocess, view='xz', params=self.cellpose_params, basename=None, savefolder=None)
            _, img_segment_3D_yz_probs, img_segment_2D_yz_flows, _ = self.useg.Cellpose2D_model_auto(
                img_preprocess, view='yz', params=self.cellpose_params, basename=None, savefolder=None)
            segmentation3D, _ = self.useg.aggregate_2D_to_3D_segmentation_direct_method(
                probs=[img_segment_3D_xy_probs, img_segment_3D_xz_probs,img_segment_3D_yz_probs],
                gradients=[img_segment_2D_xy_flows, img_segment_2D_xz_flows, img_segment_2D_yz_flows],
                params=self.aggreg_params, savefolder=None, basename=None)
            return segmentation3D
