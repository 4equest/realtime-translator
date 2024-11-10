import cv2
import numpy as np
import io
import time
import tasks.util.logger as logger
import tasks.util.config as config
from PIL import Image, ImageFont, ImageDraw
from .overlay_text import OverlayText
from .text_ocr.vision_ocr import TextOcrVisionOcr
from .text_ocr.vision_read import TextOcrVisionRead

class ImageProcessor:
    def __init__(self, azure_services, enable_datasaver = False, target_language = config.value_of("target_language"), ocr_method = config.value_of("ocr_method")):
        self.azure_services = azure_services
        self.overlay_text = OverlayText(self.azure_services)
        self.text_ocr_vision_ocr = TextOcrVisionOcr(self.azure_services)
        self.text_ocr_vision_read = TextOcrVisionRead(self.azure_services)
        self.overlay_image = None
        self.enable_datasaver = enable_datasaver
        self.target_language = target_language
        self.ocr_method = ocr_method
        
    def prepare_overlay(self, image_buffer: io.BufferedReader) -> Image:

        if self.ocr_method == "vision_read":
            ocr_instance  = self.text_ocr_vision_read
        elif self.ocr_method == "vision_ocr":
            ocr_instance  = self.text_ocr_vision_ocr
        else:
            raise ValueError(f"Invalid OCR method: {self.ocr_method}")
            
        ocr_result = ocr_instance.run(image_buffer)
        image = Image.open(image_buffer)
        return self.overlay_text.draw_text(image, ocr_result, self.target_language)
    
    def process_image(self, image_buffer: io.BufferedReader) -> Image:
        logger.info(f"new ocr task")
        self.task_time_start = time.perf_counter()
        self.overlay_image = self.prepare_overlay(image_buffer)
        time_end = time.perf_counter()
        logger.info(f"ocr cost {time_end- self.task_time_start}s")

        return self.overlay_image
    