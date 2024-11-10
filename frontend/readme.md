# Frontend

## Setup
1. 仮想環境を作成
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. 設定
instance内の`api_keys.json`を編集し、任意のAPIキーを設定してください。Clientで利用します。
必要に応じて環境変数にRedisの接続情報を設定してください。

3. 実行
```
python3 run.py
```