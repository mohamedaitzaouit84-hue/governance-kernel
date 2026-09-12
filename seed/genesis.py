"""seed/genesis.py — لحظة إنشاء البذرة. تُشغَّل مرة واحدة فقط."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import root


def main():
    print("Genesis — إنشاء البذرة")
    print("=" * 50)
    try:
        root.generate_owner_key()
        print("OK: تم توليد مفتاح المالك (Ed25519)")
    except RuntimeError as e:
        print(f"WARN: {e} — لن يتم إعادة التوليد.")
    state = root.record_root_state()
    print(f"OK: بصمة المفتاح: {state['owner_key_fingerprint']}")
    print(f"OK: تاريخ الإنشاء: {state['created_at']}")
    print("=" * 50)
    print("البذرة جاهزة. لم تنبت بعد.")


if __name__ == "__main__":
    main()
