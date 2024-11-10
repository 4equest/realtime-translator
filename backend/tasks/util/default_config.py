default_config = {
    "vision_key": "default_vision_key",
    "vision_endpoint": "default_vision_endpoint",
    "translator_key": "default_translator_key",
    "translator_endpoint": "https://api.cognitive.microsofttranslator.com/",
    "log_dir": "logs",
    "log_level": "DEBUG",
    "target_language": "ja", #https://learn.microsoft.com/ja-jp/azure/ai-services/translator/language-support
    "ocr_method": "vision_read",
    "ocr_read_operation_check_interval": 0.3,
    "debug_mode": False, #画面をフルスクリーンじゃなくて半分サイズのウィンドで表示
    "font_url": "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/JP/SourceHanSansJP-Medium.otf",
    "font_path": "fonts/SourceHanSansJP-Medium.otf",
    "redis_broker_url": "redis://localhost:6379/0",
    "redis_backend_url": "redis://localhost:6379/0"
}

valid_values = {
    "log_level": ["FRAME", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    "ocr_method": ["vision_read", "vision_ocr", "document"],
}