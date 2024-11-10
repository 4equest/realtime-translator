import os
import base64
from io import BytesIO

from flask import Blueprint, request, jsonify, send_file, abort
from .auth import verify_api_key
from . import cache
from celery import Celery

api_bp = Blueprint('api', __name__)

celery = Celery(
    'frontend',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')
)

@api_bp.before_request
def authenticate():
    """全てのAPIリクエストで認証"""
    api_key = request.headers.get('Authorization')
    if not verify_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

@api_bp.route('/upload', methods=['POST'])
def upload_image():
    """画像データを受け取り、非同期処理"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    params = request.args.to_dict()
    print(params)
    image_data = base64.b64encode(file.read()).decode('utf-8')  # バイナリをBase64にエンコード
    
    # タスクのキューイング
    task = celery.send_task('tasks.tasks.process_image_task', args=[image_data, params])
    return jsonify({"job_id": task.id}), 202

@api_bp.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """処理結果のURLを取得"""
    result = celery.AsyncResult(job_id)
    if result.state == 'SUCCESS':
        # 処理完了時に画像データをキャッシュに保存
        cache.set(job_id, result.result)
        image_url = f"/image/{job_id}"
        return jsonify({"status": "completed", "image_url": image_url})
    elif result.state == 'PENDING':
        return jsonify({"status": "processing"}), 202
    else:
        return jsonify({"status": "error"}), 500

@api_bp.route('/cancel/<job_id>', methods=['GET'])
def cancel_job(job_id):
    """ジョブをキャンセル"""
    celery.control.revoke(job_id, terminate=True)
    return jsonify({"status": "cancelled"}), 200

@api_bp.route('/image/<job_id>', methods=['GET'])
def get_image(job_id):
    """キャッシュから画像データを取得して返す"""
    image_data = cache.get(job_id)
    if not image_data:
        abort(404, description="Image not found")
    
    # Base64データをデコードしてバイナリ形式で送信
    image_bytes = BytesIO(base64.b64decode(image_data))
    return send_file(image_bytes, mimetype='image/png')
