"""seed/root.py — Trust Anchor للبذرة."""
import os, stat, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

KERNEL_DIR = Path.home() / "governance_kernel"
IDENTITY_DIR = KERNEL_DIR / "identity"
OWNER_KEY_PRIV = IDENTITY_DIR / "owner_key.priv"
OWNER_KEY_PUB = IDENTITY_DIR / "owner_key.pub"
ROOT_STATE = IDENTITY_DIR / "root_state.json"


def generate_owner_key():
    IDENTITY_DIR.mkdir(parents=True, exist_ok=True)
    if OWNER_KEY_PRIV.exists():
        raise RuntimeError("مفتاح المالك موجود مسبقاً.")
    private_key = Ed25519PrivateKey.generate()
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    OWNER_KEY_PRIV.write_bytes(priv_bytes)
    OWNER_KEY_PUB.write_bytes(pub_bytes)
    os.chmod(OWNER_KEY_PRIV, stat.S_IRUSR | stat.S_IWUSR)
    os.chmod(OWNER_KEY_PUB, stat.S_IRUSR | stat.S_IWUSR)
    return private_key


def load_owner_key():
    if not OWNER_KEY_PRIV.exists():
        raise FileNotFoundError("لم يتم توليد مفتاح المالك بعد.")
    return serialization.load_pem_private_key(OWNER_KEY_PRIV.read_bytes(), password=None)


def sign(data: bytes) -> bytes:
    return load_owner_key().sign(data)


def verify(data: bytes, signature: bytes) -> bool:
    if not OWNER_KEY_PUB.exists():
        return False
    pub = serialization.load_pem_public_key(OWNER_KEY_PUB.read_bytes())
    try:
        pub.verify(signature, data)
        return True
    except Exception:
        return False


def fingerprint() -> str:
    return hashlib.sha256(OWNER_KEY_PUB.read_bytes()).hexdigest()[:16]


def record_root_state():
    state = {
        "kernel_version": "0.1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "owner_key_fingerprint": fingerprint(),
        "note": "هذا الجذر ثابت. أي تغيير فيه يبطل النظام."
    }
    ROOT_STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    return state
