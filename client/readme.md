# Client

## 動作環境
外部からの映像を受け取るにはHDMI入力のためのキャプチャカードが必要です。

## Setup
1. 仮想環境を作成
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. config.jsonの編集
config.jsonを編集し、APIキーを設定してください。
APIキーはFrontendで設定するものと同一である必要があります。
`target_language`はBCP-47言語タグで設定してください。
```json
{
    "backend_api_key": "HD-1234567890123456-MAGIC",
    "backend_url": "http://localhost:5000/api",
    "log_dir": "logs",
    "log_level": "DEBUG",
    "target_language": "ja",
    "always_ocr": true,
    "ocr_method": "vision_read",
    "ocr_operation_check_interval": 0.3,
    "enable_datasaver": false,
    "camera_device_id": 0,
    "debug_mode": true,
    "overlay_alpha": 200,
    "audio_channels": 2,
    "audio_sample_rate": 48000,
    "audio_buffer_size": 1024
}
```

3. 実行
```
python3 src/main.py
```

### 自動実行
Raspberry Piなどで、HDMIと電源をつないだだけで使えるようにするには、自動実行を可能にする必要があります。
Raspberry Piの場合は、以下のようにserviceファイルを作成します。
```service
[Unit]
Description=Real-time translation system in video stream
# After=network-online.target graphical.target

[Service]
Type=simple
User=USER_NAME
Environment="DISPLAY=:0"
Environment="XDG_RUNTIME_DIR=/run/user/1000"
WorkingDirectory=CLIENT_INSTALL_PATH
ExecStart=/usr/bin/python3 CLIENT_INSTALL_PATH/src/main.py
#Restart=on-failure
TimeoutStopSec=30

[Install]
WantedBy=graphical.target
```
