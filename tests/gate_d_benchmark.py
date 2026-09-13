"""tests/gate_d_benchmark.py — Gate D: Structural Grid.

يقيس أداء الشبكة على أحجام: 10, 50, 100 عقدة.
المقاييس: add_node, add_edge, traverse, verify — بالمللي ثانية.

يعيد تقريراً قابلاً للتسجيل في docs/GATE_D_report.md.
"""
import sys
import time
import json
import statistics
from pathlib import Path

_here = Path(__file__).resolve().parent
_kernel = _here.parent

sys.path.insert(0, str(_kernel / "memory"))
sys.path.insert(0, str(_kernel / "memory" / "semantic"))
sys.path.insert(0, str(_kernel / "memory" / "episodic"))
sys.path.insert(0, str(_kernel / "audit"))

import graph as g
import traversal as t
import event_log as ev

SIZES = [10, 50, 100]


def _reset_memory():
    """يمسح ملفات الذاكرة لإعادة البناء."""
    DATA = _kernel / "memory" / "data"
    if DATA.exists():
        for f in DATA.glob("*.jsonl"):
            f.unlink()
        for f in DATA.glob("*.json"):
            f.unlink()
    # تصفير كاش
    g._NODES = None
    g._EDGES = None
    ev._EVENTS = None
    ev._INDEX = None


def _time_ms(func):
    start = time.perf_counter()
    result = func()
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed, result


def build_graph(n):
    """يبني شبكة بـ n عقد + ~n-1 خيوط."""
    node_ids = []
    add_node_times = []

    for i in range(n):
        elapsed, nid = _time_ms(
            lambda i=i: g.add_node(f"n{i}", {"i": i})
        )
        node_ids.append(nid)
        add_node_times.append(elapsed)

    add_edge_times = []
    # ربط كل عقدة بأخرى (خطي، بدون تعقيد مفرط)
    for i in range(1, n):
        elapsed, _ = _time_ms(
            lambda i=i: g.add_edge(
                node_ids[i - 1], node_ids[i],
                relation="next", weight=0.5
            )
        )
        add_edge_times.append(elapsed)

    # إضافة بعض الحلقات القصيرة لزيادة التعقيد
    loop_count = max(1, n // 10)
    for k in range(loop_count):
        i = (k * 7) % (n - 2)
        j = (k * 11) % (n - 2)
        if i != j:
            _time_ms(
                lambda i=i, j=j: g.add_edge(
                    node_ids[i], node_ids[j + 1],
                    relation="skip", weight=0.3
                )
            )

    return node_ids, add_node_times, add_edge_times


def measure_traverse(start_id):
    """يقيس زمن كل استراتيجية اجتياز."""
    results = {}
    for strat in ["BFS", "DFS", "BY_WEIGHT", "BY_RECENCY", "BY_IMPORTANCE"]:
        elapsed, order = _time_ms(
            lambda s=strat: t.traverse(start_id, strategy=s, max_depth=20)
        )
        results[strat] = {
            "ms": round(elapsed, 3),
            "visited": len(order),
        }
    return results


def measure_verify():
    elapsed, result = _time_ms(lambda: g.verify_all())
    return {
        "ms": round(elapsed, 3),
        "ok": result["ok"],
        "nodes": result["nodes"]["total"],
        "edges": result["edges"]["total"],
    }


def bench_size(n):
    """يقيس كل المقاييس لحجم واحد."""
    print(f"\n=== Size {n} ===")
    _reset_memory()

    node_ids, add_node_times, add_edge_times = build_graph(n)

    stats = g.stats()
    print(f"  built: {stats['nodes']} nodes, {stats['edges']} edges")

    # اجتياز
    start = node_ids[0]
    trav_results = measure_traverse(start)
    for s, r in trav_results.items():
        print(f"  traverse {s:15s}: {r['ms']:7.3f} ms, visited={r['visited']}")

    # verify
    verify_result = measure_verify()
    print(f"  verify: {verify_result['ms']:.3f} ms, ok={verify_result['ok']}")

    return {
        "size": n,
        "nodes": stats["nodes"],
        "edges": stats["edges"],
        "add_node": {
            "mean_ms": round(statistics.mean(add_node_times), 3),
            "median_ms": round(statistics.median(add_node_times), 3),
            "max_ms": round(max(add_node_times), 3),
            "total_ms": round(sum(add_node_times), 3),
        },
        "add_edge": {
            "mean_ms": round(statistics.mean(add_edge_times), 3),
            "median_ms": round(statistics.median(add_edge_times), 3),
            "max_ms": round(max(add_edge_times), 3),
            "total_ms": round(sum(add_edge_times), 3),
        },
        "traverse": trav_results,
        "verify": verify_result,
    }


def main():
    print("=" * 60)
    print("Gate D — Structural Grid Benchmark")
    print("=" * 60)

    all_results = []
    for n in SIZES:
        result = bench_size(n)
        all_results.append(result)

    # تقرير نهائي
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    print()
    print(f"{'Size':>6} | {'add_node':>12} | {'add_edge':>12} | {'BFS':>10} | {'verify':>10}")
    print("-" * 60)
    for r in all_results:
        print(f"{r['size']:>6} | "
              f"{r['add_node']['mean_ms']:>10.3f}ms | "
              f"{r['add_edge']['mean_ms']:>10.3f}ms | "
              f"{r['traverse']['BFS']['ms']:>8.3f}ms | "
              f"{r['verify']['ms']:>8.3f}ms")

    # حفظ النتائج
    out_path = _kernel / "docs" / "gate_d_raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\nraw results saved: {out_path}")

    # تنظيف
    _reset_memory()


if __name__ == "__main__":
    main()
