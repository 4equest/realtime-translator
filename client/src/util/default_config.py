default_config = {
    "backend_api_key": "default_backend_api_key",
    "backend_url": "http://localhost:5000/api",
    "log_dir": "logs",
    "log_level": "DEBUG",
    "target_language": "ja", #https://learn.microsoft.com/ja-jp/azure/ai-services/translator/language-support
    "always_ocr": False,    #無料版は毎分20回までとかの制限があるので非推奨
    "ocr_method": "vision_read",
    "ocr_interval": 10,
    "ocr_operation_check_interval": 0.3,
    "enable_datasaver": False, #enable_resize
    "camera_device_id": 0, #ラズパイでやるなら固定だと思いたい
    "debug_mode": False, #画面をフルスクリーンじゃなくて半分サイズのウィンドで表示
    "overlay_alpha": 200,
    "audio_channels": 2,
    "audio_sample_rate": 48000,
    "input_device_index": 0,
    "output_device_index": 1,
    "audio_buffer_size": 1024,
}

valid_values = {
    "log_level": ["FRAME", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    "ocr_method": ["vision_read", "vision_ocr", "document"],
}