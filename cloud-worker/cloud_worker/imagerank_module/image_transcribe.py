import logging
from io import BytesIO
from pathlib import Path
from typing import TextIO, Union

from clip_interrogator import Config, Interrogator
from PIL import Image

logging.basicConfig(format='%(asctime)s %(name)s-%(levelname)s|%(lineno)d:  %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

class ImageInterrogator:
    log.info("Loading CLIP Model...")
    interrogator = Interrogator(Config(clip_model_name="ViT-L-14/openai"))
    log.info("Loading CLIP Model completed...")

    
    @classmethod
    def load_model(cls):
        if not cls.interrogator:
            cls.interrogator = Interrogator(Config(clip_model_name="ViT-L-14/openai"))
    
    @classmethod
    def convert_image_to_text(cls, fileobj: Union[str, Path, bytes, BytesIO]):
        #cls.load_model()
        
        try:
            image = Image.open(fileobj).convert('RGB')
            log.info(image)
            image_text = cls.interrogator.interrogate_fast(image)
            return ','.join(image_text.split(',')[:2])
            
        except:
            log.exception('Exception while trying to run CLIP on an image')
        
