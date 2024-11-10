# Backend

## Setup
1. Redisをインストール
```
apt update && apt install redis-server
```

2. 仮想環境を作成

ここからの作業は、分散するホストの数だけ行ってください。
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. 設定
`config.json`を編集し、Azure AIのAPIキーとエンドポイントを設定してください。
`target_language`はBCP-47言語タグで設定してください。この設定はクライアントの要求によって上書き可能です。
`redis_broker_url`と`redis_backend_url`を必要に応じて設定してください。
```json
{
    "vision_key": VISION_KEY,
    "vision_endpoint": VISION_ENDPOINT,
    "translator_key": TRANSLATOR_KEY,
    "translator_endpoint": TRANSLATOR_ENDPOINT,
    "log_dir": "logs",
    "log_level": "DEBUG",
    "target_language": "ja",
    "ocr_method": "vision_read",
    "ocr_read_operation_check_interval": 0.6,
    "debug_mode": false,
    "font_url": "https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/JP/SourceHanSansJP-Medium.otf",
    "font_path": "fonts/SourceHanSansJP-Medium.otf",
    "overlay_alpha": 200,
    "redis_broker_url": "redis://localhost:6379/0",
    "redis_backend_url": "redis://localhost:6379/0"
}
```

4. 実行

Redis サーバーの起動
```
redis-server
```
Workerの起動
```
celery -A tasks.tasks worker --loglevel=info
```

