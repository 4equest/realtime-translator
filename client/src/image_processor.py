
import io
import time
import asyncio
import threading

import cv2
import numpy as np
import requests
from PIL import Image

import util.logger as logger
import util.config as config

class ImageProcessor:
    def __init__(self):
        self.overlay_cache = None
        self.ocr_tasks = []
        self.last_process_frame_time = 0
        self.task_time_start = 0
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.thread.start()
        
    def __del__(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        
    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        
        
    def upload_image(self, image_buffer):
        files = {'file': image_buffer}
        params = {
            "enable_datasaver": config.value_of("enable_datasaver"),
            "target_language": config.value_of("target_language"),
            "ocr_method": config.value_of("ocr_method")
        }
        headers = {'Authorization': config.value_of('backend_api_key')}
        response = requests.post(f"{config.value_of('backend_url')}/upload", files=files, headers=headers, params=params)
        if response.status_code == 202:
            job_id = response.json().get("job_id")
            logger.info(f"Image uploaded successfully. Job ID: {job_id}")
            return job_id
        else:
            logger.error(f"Failed to upload image. Error: {response.text}")
            return None

    def check_job_status(self, job_id):
        headers = {'Authorization': config.value_of('backend_api_key')}
        response = requests.get(f"{config.value_of('backend_url')}/result/{job_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "completed":
                return data.get("image_url")
        elif response.status_code == 202:
            logger.debug("Job is still processing...")
            return None
        else:
            logger.error(f"Error checking job status. Status code: {response.status_code}")
            return None

    def download_image(self, image_url) -> bytes:
        headers = {'Authorization': config.value_of('backend_api_key')}
        response = requests.get(f"{config.value_of('backend_url')}{image_url}", headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to download image. Status code: {response.status_code}")
            return None


    async def prepare_overlay_cache(self, frame) -> Image:
        # 540pに縮小して画像をAzureのOCRサービスに送信
        ratio = 1.0
        if config.value_of("enable_datasaver"):
            resized_frame, ratio, _ = self.resize_image(frame, (960, 540))
            logger.frame(f"image size: {ratio}")
        else:
            resized_frame = frame
            
        _, buffer = cv2.imencode(".png", resized_frame)

        image_buffer = io.BufferedReader(io.BytesIO(buffer))
            
        job_id = self.upload_image(image_buffer)
        if not job_id:
            return
        
        logger.debug("Checking job status...")
        image_url = None
        while not image_url:
            time.sleep(config.value_of("ocr_operation_check_interval"))
            image_url = self.check_job_status(job_id)
        logger.debug(image_url)
        
        image_buffer = self.download_image(image_url)
        if not image_buffer:
            return None
        
        # bytes to image
        image = Image.open(io.BytesIO(image_buffer))
        
        return image
    
    def process_frame(self, frame):
        time_start = time.perf_counter()
        
        if config.value_of("always_ocr") and len(self.ocr_tasks) == 0:
            self.ocr_tasks.append([asyncio.run_coroutine_threadsafe(self.prepare_overlay_cache(frame), self.loop), time.perf_counter()])
            logger.info(f"new ocr task {self.ocr_tasks[-1]}")

        if not config.value_of("always_ocr") and time_start - self.last_process_frame_time >= config.value_of("ocr_interval"):
            self.last_process_frame_time = time_start
            self.ocr_tasks.append([asyncio.run_coroutine_threadsafe(self.prepare_overlay_cache(frame), self.loop), time.perf_counter()])
            logger.info(f"new ocr task {self.ocr_tasks[-1]}")
            
        completed_tasks = []
        for task in self.ocr_tasks:
            if task and task[0].done():
                self.overlay_cache = task[0].result()
                time_end = time.perf_counter()
                logger.info(f"ocr cost {time_end- task[1]}s")
                completed_tasks.append(task)
        for task in completed_tasks:
            self.ocr_tasks.remove(task)

        if self.overlay_cache is not None:
            frame = Image.fromarray(frame)
            frame = Image.alpha_composite(frame.convert('RGBA'), self.overlay_cache)
            frame = np.array(frame)

        return frame

