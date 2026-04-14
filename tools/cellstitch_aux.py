import numpy as np

def apply_model(model, model_type, imgs, model_parameters):
    if model_type == "StitchSD2D":
        return np.array([model.predict_instances(img, **model_parameters)[0] for img in imgs])
    if model_type == "StitchCP2D":
        return np.array(model.eval(list(imgs), **model_parameters)[0])

def post_process(mask, min_volume = 27, min_thickness = 2):
    final_mask = np.zeros_like(mask, dtype=np.uint16)
    mask_idx = np.unique(mask)[1:]

    nb_mask = 1
    for idx in mask_idx:
        crt_mask = ((mask == idx)*1).astype(np.uint16)
        # Check for min thickness of the mask
        X, Y, Z = np.nonzero(crt_mask)
        thickness = min(max(X)-min(X), max(Y)-min(Y), max(Z)-min(Z))

        volume = crt_mask.sum()

        if thickness>=min_thickness and volume>=min_volume:
            #print(f"final mask : {final_mask.dtype}, crt mask : {crt_mask.dtype}, nb mask : {type(nb_mask)}")
            final_mask += crt_mask*nb_mask
            nb_mask += 1

    return final_mask