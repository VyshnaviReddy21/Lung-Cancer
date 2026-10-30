"""Fail-closed SavedModel adapter. No training/preprocessing defaults."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
EXPECTED_CLASSES = {'adenocarcinoma', 'large.cell.carcinoma', 'normal', 'squamous.cell.carcinoma'}
class ModelUnavailable(RuntimeError): pass

def validate_manifest(manifest):
    required = {'verified_from_training', 'classes', 'input_name', 'output_name', 'height', 'width', 'channels', 'dtype', 'color_order', 'interpolation', 'preprocessing', 'output_semantics'}
    if not required.issubset(manifest) or manifest['verified_from_training'] is not True:
        raise ModelUnavailable('A training-verified model manifest is required.')
    if len(manifest['classes']) != 4 or set(manifest['classes']) != EXPECTED_CLASSES:
        raise ModelUnavailable('Verify the four output classes and their training order.')
    if manifest['channels'] not in (1, 3) or manifest['dtype'] != 'float32':
        raise ModelUnavailable('Unsupported input contract; adapt using verified training code.')
    if manifest['preprocessing'] not in ('none', 'divide_255', 'minus_one_one'):
        raise ModelUnavailable('Custom preprocessing must be supplied from the training code.')
    if manifest['color_order'] not in ('RGB', 'BGR', 'GRAY') or manifest['interpolation'] not in ('nearest', 'bilinear', 'bicubic'):
        raise ModelUnavailable('Unsupported color or resize contract.')
    if (manifest['channels'] == 1) != (manifest['color_order'] == 'GRAY'):
        raise ModelUnavailable('Channel count and color order do not agree.')
    if manifest['output_semantics'] not in ('probabilities', 'logits'):
        raise ModelUnavailable('Verify whether the outputs are probabilities or logits.')
    for key in ('height', 'width'):
        if not isinstance(manifest[key], int) or not 1 <= manifest[key] <= 4096:
            raise ModelUnavailable('Invalid input dimensions.')
    return manifest

def probabilities(raw, semantics):
    values = np.asarray(raw, dtype=np.float64).reshape(-1)
    if values.size != 4 or not np.isfinite(values).all():
        raise ModelUnavailable('The model returned invalid class outputs.')
    if semantics == 'logits':
        values = np.exp(values - values.max()); values /= values.sum()
    if (values < 0).any() or (values > 1).any() or not np.isclose(values.sum(), 1, atol=1e-3):
        raise ModelUnavailable('The model did not return valid probabilities.')
    return values

class SavedModelService:
    def __init__(self, config):
        self.ready = False; self.reason = 'Model has not been configured.'; self.config = config
        try:
            directory = Path(config['AI_MODEL_PATH'])
            if not config['AI_MODEL_PATH'] or not (directory / 'saved_model.pb').is_file() or not (directory / 'variables').is_dir() or not (directory / 'assets').is_dir():
                raise ModelUnavailable('Supply the complete SavedModel directory: saved_model.pb, variables/, and assets/.')
            if not config['MODEL_MANIFEST_PATH'] or not config['MODEL_VERSION']:
                raise ModelUnavailable('Supply MODEL_MANIFEST_PATH and MODEL_VERSION verified against training.')
            self.manifest = validate_manifest(json.loads(Path(config['MODEL_MANIFEST_PATH']).read_text()))
            import tensorflow as tf
            self.tf = tf; self.model = tf.saved_model.load(str(directory))
            self.fn = self.model.signatures.get('serving_default')
            if self.fn is None: raise ModelUnavailable('SavedModel has no serving_default signature.')
            inputs = self.fn.structured_input_signature[1]; m = self.manifest
            if len(inputs) != 1 or m['input_name'] not in inputs: raise ModelUnavailable('Manifest input name does not match serving_default.')
            spec = inputs[m['input_name']]
            if spec.dtype.name != m['dtype'] or spec.shape.as_list() not in ([None,m['height'],m['width'],m['channels']], [1,m['height'],m['width'],m['channels']]):
                raise ModelUnavailable('Input shape/dtype differs from training manifest.')
            if m['output_name'] not in self.fn.structured_outputs: raise ModelUnavailable('Manifest output name is not exported.')
            self.ready = True; self.reason = 'Loaded verified serving_default signature.'
        except ModelUnavailable as error: self.reason = str(error)
        except Exception: self.reason = 'Model load failed. Check artifact compatibility and server diagnostics.'
    def predict(self, image_path):
        if not self.ready: raise ModelUnavailable(self.reason)
        m = self.manifest
        filters = {'nearest':Image.Resampling.NEAREST, 'bilinear':Image.Resampling.BILINEAR, 'bicubic':Image.Resampling.BICUBIC}
        with Image.open(image_path) as image:
            image = image.convert('L' if m['channels']==1 else 'RGB').resize((m['width'],m['height']), filters[m['interpolation']])
            arr = np.asarray(image,dtype=np.float32)
        if m['channels']==1: arr = arr[...,None]
        elif m['color_order']=='BGR': arr = arr[...,::-1]
        if m['preprocessing']=='divide_255': arr /= 255.0
        elif m['preprocessing']=='minus_one_one': arr = arr / 127.5 - 1.0
        output = self.fn(**{m['input_name']:self.tf.convert_to_tensor(arr[None,...])})[m['output_name']].numpy()
        p = probabilities(output,m['output_semantics']); index = int(p.argmax())
        return {'label':m['classes'][index], 'confidence':float(p[index]), 'probabilities':dict(zip(m['classes'],map(float,p))), 'model_version':self.config['MODEL_VERSION'], 'gradcam_status':'unavailable', 'gradcam_reason':'serving_default does not expose a verified differentiable feature-map path.'}
