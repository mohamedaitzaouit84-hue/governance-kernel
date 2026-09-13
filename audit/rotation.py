"""audit/rotation.py — تدوير تلقائي للسجل.

الاستراتيجية:
- عندما يبلغ audit.jsonl حجم MAX_RECORDS سجلاً،
  يُنقل إلى audit-YYYYMMDD-HHMMSS.jsonl
- يُبدأ ملف جديد بـ Genesis + آخر hash من الملف السابق
- يُكتب manifest يُوثّق الانتقال

الحد الافتراضي: 5000 سجلاً.
"""
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

_here = Path(__file__).resolve().parent
_kernel = _here.parent

sys.path.insert(0, str(_here))

KERNEL_DIR = _kernel
LOG_PATH = KERNEL_DIR / "logs" / "audit.jsonl"
ARCHIVE_DIR = KERNEL_DIR / "logs" / "archive"
MANIFEST = KERNEL_DIR / "logs" / "rotation_manifest.jsonl"

MAX_RECORDS = 5000
KEEP_ARCHIVED = 10  # عدد الملفات المؤرشفة التي نحتفظ بها


def _now():
    return datetime.now(timezone.utc).isoformat()


def _stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _count_records():
    if not LOG_PATH.exists():
        return 0
    n = 0
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def _last_record():
    if not LOG_PATH.exists():
        return None
    last = None
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                last = json.loads(line)
    return last


def _rotate():
    """نقل السجل الحالي إلى الأرشيف، بدء سجل جديد."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    archive_path = ARCHIVE_DIR / f"audit-{stamp}.jsonl"

    last = _last_record()
    if last is None:
        return None

    shutil.move(str(LOG_PATH), str(archive_path))

    # بدء ملف جديد. كل ملف مستقل — prev_hash = "0"*64.
    # الربط بالملف السابق يُوثَّق في manifest + data.
    from append_only_log import _hash_record, _write_record, GENESIS_HASH
    ts = _now()
    data = {
        "note": "continuation after rotation",
        "previous_archive": archive_path.name,
        "previous_last_hash": last["hash"],
        "previous_last_seq": last["seq"],
    }
    prev = GENESIS_HASH
    h = _hash_record(0, ts, prev, "rotation_continuation", data)
    rec = {
        "seq": 0,
        "ts": ts,
        "prev_hash": prev,
        "kind": "rotation_continuation",
        "data": data,
        "hash": h,
    }
    _write_record(rec)

    # كتابة manifest
    manifest_entry = {
        "ts": _now(),
        "archived": archive_path.name,
        "previous_last_seq": last["seq"],
        "previous_last_hash": last["hash"],
        "new_genesis_hash": h,
    }
    with open(MANIFEST, "a", encoding="utf-8") as f:
        f.write(json.dumps(manifest_entry, ensure_ascii=False,
                           separators=(",", ":")) + "\n")

    # تنظيف الأرشيف القديم
    _cleanup_archive()

    return manifest_entry


def _cleanup_archive():
    """يحتفظ بآخر KEEP_ARCHIVED ملفات فقط."""
    files = sorted(ARCHIVE_DIR.glob("audit-*.jsonl"))
    if len(files) > KEEP_ARCHIVED:
        to_delete = files[:-KEEP_ARCHIVED]
        for f in to_delete:
            f.unlink()


def check_and_rotate():
    """يُستدعى دورياً. يُدوّر إذا تجاوز الحد."""
    n = _count_records()
    if n < MAX_RECORDS:
        return {"rotated": False, "records": n, "max": MAX_RECORDS}
    result = _rotate()
    return {
        "rotated": True,
        "records_before": n,
        "max": MAX_RECORDS,
        "manifest": result,
    }


def status():
    files = sorted(ARCHIVE_DIR.glob("audit-*.jsonl")) if ARCHIVE_DIR.exists() else []
    return {
        "current_records": _count_records(),
        "max_records": MAX_RECORDS,
        "archived_files": len(files),
        "keep_archived": KEEP_ARCHIVED,
    }


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif len(_sys.argv) > 1 and _sys.argv[1] == "check":
        print(json.dumps(check_and_rotate(), indent=2, ensure_ascii=False))
    elif len(_sys.argv) > 1 and _sys.argv[1] == "force":
        result = _rotate()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python audit/rotation.py [status|check|force]")
