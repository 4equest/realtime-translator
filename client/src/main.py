import os
import cv2
import time
import asyncio
import util.config as config
import util.logger as logger
from hardware.button import Button
from image_processor import ImageProcessor

if os.name == 'nt':
    from audio.processor_win import AudioProcessor
else:
    from audio.processor_linux import AudioProcessor
    

def main():
    if os.name != 'nt':
        hardware_button = Button(18)
        
    audio_processor = AudioProcessor()
    image_processor = ImageProcessor()
    
    cap = cv2.VideoCapture(config.value_of("camera_device_id"))
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    width = 1920
    height = 1080
    FPS = 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if config.value_of("debug_mode"):
        cv2.namedWindow("main")
    else:
        cv2.namedWindow("main",cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("main",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    audio_processor.start()
    WAIT_TIME_BASE = 1.0 / FPS

    while True:
        time_start = time.perf_counter()
        try:
            ret, frame = cap.read()
            if not ret:
                logger.error(f"Capture error: {ret}")
                break
        except:
            print("error")
        
        if os.name != 'nt':
            if hardware_button.has_pushed():
                frame = image_processor.process_frame(frame)
        else:
            frame = image_processor.process_frame(frame)
        
        if config.value_of("debug_mode"):
            # デバッグのために表示画面のサイズは半分にする
            height, width = frame.shape[:2]
            new_width = int(width * 0.5)
            new_height = int(height * 0.5)
            frame = cv2.resize(frame, (new_width, new_height))

        cv2.imshow("main", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        

        time_end = time.perf_counter()
        # logger.info(f"sleep: {WAIT_TIME_BASE-(time_end-time_start)}")
        time.sleep(max(WAIT_TIME_BASE - (time_end- time_start) / 1000, 0.0))
        
    if cap is not None:
        cap.release()
    
    if audio_processor is not None:
        audio_processor.stop()
        
    cv2.destroyAllWindows()

    config.release()
    
    
if __name__ == "__main__":
    main()