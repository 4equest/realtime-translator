import json

API_KEYS_FILE = './instance/api_keys.json'

def verify_api_key(api_key):
    """APIキーの認証"""
    if not api_key:
        return False
    try:
        with open(API_KEYS_FILE, 'r') as f:
            valid_keys = json.load(f)
        return api_key in valid_keys.get("keys", [])
    except Exception as e:
        return False