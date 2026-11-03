import json
from pathlib import Path
STORE=Path(__file__).resolve().parents[1]/'data/users.json'
def signup(email,password):
    if not email or not password:
        return False
    users=json.loads(STORE.read_text()) if STORE.exists() else {}
    if email in users:
        return False
    users[email]=password
    STORE.parent.mkdir(exist_ok=True)
    STORE.write_text(json.dumps(users))
    return True
def login(email,password):
    users=json.loads(STORE.read_text()) if STORE.exists() else {}
    return email in users and users[email]==password
