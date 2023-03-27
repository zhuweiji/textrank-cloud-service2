import logging
from pathlib import Path
from typing import TextIO

from clip_interrogator import Config, Interrogator
from PIL import Image

log = logging.getLogger(__name__)

class ImageInterrogator:
    interrogator = Interrogator(Config(clip_model_name="ViT-L-14/openai"))
    
    @classmethod
    def convert_image_to_text(cls, filepath: Path):
        try:
            image = Image.open(filepath).convert('RGB')
            log.info(image)
            image_text = cls.interrogator.interrogate_fast(image)
            return image_text
        except:
            log.exception('Exception while trying to run CLIP on an image')
        

