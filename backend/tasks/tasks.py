import time
from celery import Celery
from PIL import Image
import base64
from io import BytesIO

from .image.azure_services import AzureServices
from .image.processor import ImageProcessor
from .util.font import download_font
import tasks.util.config as config
import tasks.util.logger as logger

download_font()

azure_services = AzureServices(
    config.value_of('vision_key'),
    config.value_of('vision_endpoint'),
    config.value_of('translator_key'),
    config.value_of('translator_endpoint')
)


    
celery = Celery(
    'tasks',
    broker=config.value_of('redis_broker_url'),
    backend=config.value_of('redis_backend_url')
)

@celery.task
def process_image_task(image_data: str, params: dict):
    """画像処理タスク"""
    
    # Base64をデコードしてPillowで読み込む
    img_buffer = BytesIO(base64.b64decode(image_data))
    enable_datasaver = params.get("enable_datasaver", False)
    target_language = params.get("target_language", config.value_of("target_language"))
    ocr_method = params.get("ocr_method", config.value_of("ocr_method"))
    logger.info(f"enable_datasaver: {enable_datasaver}, target_language: {target_language}, ocr_method: {ocr_method}")
    image_processor = ImageProcessor(azure_services, enable_datasaver, target_language, ocr_method)

    img = image_processor.process_image(img_buffer)
    
    # 再度Base64にエンコード
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    processed_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return processed_data