"""교육용 파일 저장입니다. 실제 서비스용이 아닙니다."""
import hashlib
import hmac
import json
from pathlib import Path
import secrets

STORE = Path(__file__).resolve().parents[1] / 'data' / 'users.json'

def _load():
    if not STORE.exists():
        return {}
    return json.loads(STORE.read_text(encoding='utf-8'))

def _save(users):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(users, ensure_ascii=False), encoding='utf-8')

def _digest(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000).hex()

def signup(email, password):
    if not email or not password:
        return False
    users = _load()
    if email in users:
        return False
    salt = secrets.token_hex(16)
    users[email] = {'salt': salt, 'digest': _digest(password, salt)}
    _save(users)
    return True

def login(email, password):
    if not email or not password:
        return False
    user = _load().get(email)
    if not user:
        return False
    return hmac.compare_digest(user['digest'], _digest(password, user['salt']))
