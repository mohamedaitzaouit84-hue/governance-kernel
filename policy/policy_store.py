"""policy/policy_store.py — تخزين السياسة وتوقيعها."""
import hashlib, sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "seed"))
import root

KERNEL_DIR = Path.home() / "governance_kernel"
POLICY_FILE = KERNEL_DIR / "policy" / "policies" / "default.yaml"
POLICY_SIG = KERNEL_DIR / "policy" / "policies" / "default.yaml.sig"


def _hash_policy(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest().encode("utf-8")


def load():
    if not POLICY_FILE.exists():
        raise FileNotFoundError(f"missing policy: {POLICY_FILE}")
    text = POLICY_FILE.read_text(encoding="utf-8")
    sig_path = POLICY_SIG
    if not sig_path.exists():
        sig = root.sign(_hash_policy(text))
        sig_path.write_text(sig.hex(), encoding="utf-8")
        print("policy signed (first load)")
    else:
        sig = bytes.fromhex(sig_path.read_text(encoding="utf-8").strip())
        if not root.verify(_hash_policy(text), sig):
            raise RuntimeError("policy signature INVALID — possible tamper")
    return yaml.safe_load(text)


def reload_and_resign():
    sig = root.sign(_hash_policy(POLICY_FILE.read_text(encoding="utf-8")))
    POLICY_SIG.write_text(sig.hex(), encoding="utf-8")
