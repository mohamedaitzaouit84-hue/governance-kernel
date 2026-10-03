"""G0.44 — Test isolation: real log untouched by test suite (J-0.8.60).

Criterion:
  Running the test suite must not modify logs/audit.jsonl or
  logs/checkpoints.jsonl in the repository. This is enforced
  by two environment variables:
    GK_LOG_PATH  -> audit log
    GK_CKPT_PATH -> checkpoints file
  Both append_only_log.py and integrity.py must honor them.

Scenarios:
  S1: With GK_LOG_PATH set, append_only_log.LOG_PATH reflects it.
  S2: Without GK_LOG_PATH, append_only_log.LOG_PATH == default.
  S3: With both set, both paths reflect env vars.
  S4: run_all.py source contains both env var names.
  S5: Subprocess with env vars set writes to sandbox only;
      real log is byte-identical before and after.

Read-only. Uses subprocesses for isolation.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent

_REAL_LOG = _REPO / "logs" / "audit.jsonl"
_REAL_CKPT = _REPO / "logs" / "checkpoints.jsonl"

_SANDBOX_ROOT = Path(os.path.expanduser("~")) / ".gk_sandbox"


def _file_hash(p):
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _probe_script():
    return (
        'import sys;'
        'sys.path.insert(0, r"{0}");'
        'sys.path.insert(0, r"{0}/audit");'
        'import append_only_log as aol;'
        'print(str(aol.LOG_PATH));'
        'print(str(aol.CKPT_PATH))'
    ).format(str(_REPO))


def _run_probe(extra_env=None):
    env = dict(os.environ)
    env.pop("GK_LOG_PATH", None)
    env.pop("GK_CKPT_PATH", None)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(
        [sys.executable, "-c", _probe_script()],
        env=env, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    lines = r.stdout.strip().splitlines()
    if len(lines) != 2:
        return None
    return (lines[0], lines[1])


def s1_env_var_redirects_log():
    probe_log = "/nonexistent/sandbox/audit.jsonl"
    out = _run_probe({"GK_LOG_PATH": probe_log})
    if out is None:
        return False
    return out[0] == probe_log


def s2_default_without_env_var():
    out = _run_probe()
    if out is None:
        return False
    return out[0] == str(_REAL_LOG)


def s3_both_redirected():
    probe_log = "/nonexistent/sandbox/audit.jsonl"
    probe_ckpt = "/nonexistent/sandbox/checkpoints.jsonl"
    out = _run_probe({"GK_LOG_PATH": probe_log, "GK_CKPT_PATH": probe_ckpt})
    if out is None:
        return False
    return out[0] == probe_log and out[1] == probe_ckpt


def s4_runall_sets_env_vars():
    runner = _HERE / "run_all.py"
    if not runner.exists():
        return False
    src = runner.read_text(encoding="utf-8")
    return ("GK_LOG_PATH" in src) and ("GK_CKPT_PATH" in src)


def s5_subprocess_isolated():
    # Guard: if mechanism not in place, do not risk pollution.
    if not s1_env_var_redirects_log():
        return False

    before_log_hash = _file_hash(_REAL_LOG)
    before_ckpt_hash = _file_hash(_REAL_CKPT)

    _SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    sandbox = Path(tempfile.mkdtemp(prefix="g044_", dir=str(_SANDBOX_ROOT)))
    sandbox_log = sandbox / "audit.jsonl"
    sandbox_ckpt = sandbox / "checkpoints.jsonl"

    code = (
        'import sys;'
        'sys.path.insert(0, r"{0}");'
        'sys.path.insert(0, r"{0}/audit");'
        'import append_only_log as aol;'
        'aol.append("g044_probe", {{"k": 1}});'
        'assert str(aol.LOG_PATH) == r"{1}", '
        '"log not redirected: " + str(aol.LOG_PATH)'
    ).format(str(_REPO), str(sandbox_log))

    env = dict(os.environ)
    env["GK_LOG_PATH"] = str(sandbox_log)
    env["GK_CKPT_PATH"] = str(sandbox_ckpt)

    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            env=env, capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("  subprocess error: {}".format(r.stderr.strip()[:200]))
            return False

        if not sandbox_log.exists() or sandbox_log.stat().st_size == 0:
            return False

        after_log_hash = _file_hash(_REAL_LOG)
        after_ckpt_hash = _file_hash(_REAL_CKPT)

        return (before_log_hash == after_log_hash) and \
               (before_ckpt_hash == after_ckpt_hash)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    checks = [
        ("S1 env var redirects log",   s1_env_var_redirects_log),
        ("S2 default without env var", s2_default_without_env_var),
        ("S3 both env vars honored",   s3_both_redirected),
        ("S4 run_all sets env vars",   s4_runall_sets_env_vars),
        ("S5 subprocess isolated",     s5_subprocess_isolated),
    ]

    passed = 0
    failed = []
    for name, fn in checks:
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            print("  {}: EXCEPTION {}".format(name, e))
        if ok:
            passed += 1
        else:
            failed.append(name)

    print("  Test isolation checks: {}/{}".format(passed, len(checks)))
    if failed:
        print("  FAILED: {}".format(failed))

    if passed == len(checks):
        print("G0.44: CLOSED ({}/{})".format(passed, len(checks)))
        return 0
    else:
        print("G0.44: FAILED ({}/{})".format(passed, len(checks)))
        return 1


if __name__ == "__main__":
    sys.exit(main())
