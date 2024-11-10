import os
from flask import Flask
from flask_caching import Cache

cache = Cache()

def create_app():
    app = Flask(__name__)
    
    # キャッシュ設定
    app.config['CACHE_TYPE'] = 'SimpleCache'  # メモリキャッシュを使用
    app.config['CACHE_DEFAULT_TIMEOUT'] = 3600  # キャッシュのデフォルト有効期限（1時間）
    cache.init_app(app)
    
    # インスタンスフォルダ設定
    app.config['INSTANCE_PATH'] = os.environ.get('INSTANCE_PATH', './instance')
    app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # ルートの登録
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app