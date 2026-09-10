#!/usr/bin/env python3
"""Realized spawn-tree checker for SwarmBench Phase 2 task packages.

Usage:
    python3 tools/check_dag.py <task_root_or_execution_logs_or_raw_trajectory_dir>

Reports, for every run directory found under execution_logs/:
  - session id / parent_id pairs with filenames
  - realized spawn-tree depth (levels of parent-child subagent invocation)
  - realized width (max siblings under one parent, max nodes per level,
    max wall-clock concurrency)
  - realized sub-agent count and per-session `task` tool spawn calls
and compares them against task.toml (dag_depth, dag_width,
estimated_sub_agents) and decomposition.yaml (depends_on level count,
parallel_group width).
"""
import json
import os
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None


def find_run_dirs(root):
    """Yield (label, raw_trajectory_dir) for every run under the given path."""
    if os.path.basename(root.rstrip("/")) == "raw_trajectory":
        yield (root, root)
        return
    hits = []
    for dirpath, dirnames, _ in os.walk(root):
        if os.path.basename(dirpath) == "raw_trajectory":
            hits.append(dirpath)
    for h in sorted(hits):
        parts = os.path.abspath(h).split(os.sep)
        if "execution_logs" in parts:
            i = parts.index("execution_logs")
            label = parts[i + 1] if len(parts) > i + 1 else "execution_logs"
        else:
            label = os.path.relpath(h, root)
        yield (label, h)


def load_sessions(traj_dir):
    sessions = {}
    for fn in sorted(os.listdir(traj_dir)):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(traj_dir, fn)
        try:
            with open(path) as fh:
                data = json.load(fh)
        except Exception as exc:
            print(f"    [warn] cannot parse {fn}: {exc}")
            continue
        if not isinstance(data, dict) or "id" not in data:
            continue
        sessions[data["id"]] = {
            "file": fn,
            "id": data["id"],
            "parent_id": data.get("parent_id"),
            "title": data.get("title") or "",
            "agent": data.get("agent"),
            "t0": data.get("time_created"),
            "t1": data.get("time_updated"),
            "task_calls": count_task_calls(data),
        }
    return sessions


def count_task_calls(session):
    """Count `task`-tool spawn calls made from this session."""
    n = 0
    for msg in session.get("messages") or []:
        for part in msg.get("parts") or []:
            if part.get("type") == "tool" and part.get("tool") == "task":
                n += 1
                continue
            data = part.get("data") if isinstance(part.get("data"), dict) else None
            if data and data.get("type") == "tool" and data.get("tool") == "task":
                n += 1
    return n


def levels(sessions):
    """Assign a level to each session: root = 0, child of root = 1, ..."""
    lvl = {}

    def depth_of(sid, seen=None):
        seen = seen or set()
        if sid in lvl:
            return lvl[sid]
        if sid in seen:
            return 0
        seen.add(sid)
        p = sessions[sid]["parent_id"]
        d = 0 if (p is None or p not in sessions) else depth_of(p, seen) + 1
        lvl[sid] = d
        return d

    for sid in sessions:
        depth_of(sid)
    return lvl


def max_concurrency(nodes):
    """Max number of sessions alive at the same instant (wall clock)."""
    events = []
    for n in nodes:
        if n["t0"] is None or n["t1"] is None:
            continue
        events.append((n["t0"], 1))
        events.append((n["t1"], -1))
    if not events:
        return None
    events.sort(key=lambda e: (e[0], -e[1]))
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best


def time_waves(nodes):
    """Group sessions into batches whose lifetimes overlap transitively.

    A flat spawn tree dispatched in dependent stages shows up as several
    non-overlapping batches; this is the realized DEPENDENCY depth even when
    every session's parent is the orchestrator.
    """
    ns = [n for n in nodes if n["t0"] is not None and n["t1"] is not None]
    if not ns:
        return []
    ns.sort(key=lambda n: n["t0"])
    waves, cur, end = [], [ns[0]], ns[0]["t1"]
    for n in ns[1:]:
        if n["t0"] <= end:
            cur.append(n)
            end = max(end, n["t1"])
        else:
            waves.append(cur)
            cur, end = [n], n["t1"]
    waves.append(cur)
    return waves


def report_run(label, traj_dir):
    sessions = load_sessions(traj_dir)
    print(f"\n=== RUN: {label}")
    print(f"    dir: {traj_dir}")
    if not sessions:
        print("    no session files found")
        return None
    lvl = levels(sessions)
    children = defaultdict(list)
    for sid, s in sessions.items():
        children[s["parent_id"]].append(sid)

    print(f"    {'file':<52} {'level':>5}  id -> parent_id  (task calls)")
    for sid, s in sorted(sessions.items(), key=lambda kv: (lvl[kv[0]], kv[1]["file"])):
        print(f"    {s['file']:<52} {lvl[sid]:>5}  {sid} -> {s['parent_id']}  ({s['task_calls']} task)")
        if s["title"]:
            print(f"        title: {s['title'][:110]}")

    per_level = defaultdict(list)
    for sid in sessions:
        per_level[lvl[sid]].append(sid)

    max_level = max(lvl.values())
    n_sub = sum(1 for s in sessions.values() if s["file"].startswith("subagent_"))
    sib_width = max((len(v) for k, v in children.items() if k in sessions), default=0)
    level_width = max((len(v) for k, v in per_level.items() if k > 0), default=0)
    conc = max_concurrency([s for sid, s in sessions.items() if lvl[sid] > 0])
    spawners = [s["file"] for s in sessions.values() if s["task_calls"] > 0]
    total_task_calls = sum(s["task_calls"] for s in sessions.values())

    print("\n    -- realized --")
    print(f"    sessions total            : {len(sessions)} (subagent files: {n_sub})")
    for k in sorted(per_level):
        print(f"    level {k} sessions          : {len(per_level[k])}")
    print(f"    realized DEPTH (levels)   : {max_level + 1} levels "
          f"(= root + {max_level} generation(s) of spawning)")
    print(f"    realized dag_depth metric : {max_level}  "
          f"(longest chain of parent->child spawns)")
    print(f"    realized WIDTH            : {level_width} (max sessions in one level > 0)")
    print(f"    max siblings one parent   : {sib_width}")
    print(f"    max wall-clock concurrency: {conc}")
    print(f"    sessions that spawned     : {len(spawners)} -> {spawners}")
    print(f"    total `task` spawn calls  : {total_task_calls}")
    waves = time_waves([s for sid, s in sessions.items() if lvl[sid] > 0])
    if waves:
        print(f"    sequential dispatch waves : {len(waves)} "
              f"(sizes {[len(w) for w in waves]})")
        print("      (non-overlapping batches of sibling sessions; a flat spawn"
              " tree can still realize dependency depth this way)")
    nested = [sid for sid in sessions if lvl[sid] >= 2]
    print(f"    nested (level>=2) agents  : {len(nested)}"
          f"{'  << flat fan-out only' if not nested else ''}")
    return {
        "label": label,
        "depth_levels": max_level + 1,
        "depth_edges": max_level,
        "width": level_width,
        "subagents": n_sub,
        "task_calls": total_task_calls,
        "nested": len(nested),
        "waves": len(waves) if waves else 0,
        "wave_sizes": [len(w) for w in waves] if waves else [],
    }


def decomposition_levels(path):
    if yaml is None:
        print("  [warn] pyyaml not installed, skipping decomposition.yaml")
        return None
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    subs = doc.get("subtasks") or doc.get("sub_tasks") or doc.get("tasks") or []
    if isinstance(subs, dict):
        subs = list(subs.values())
    ids = {}
    for s in subs:
        if not isinstance(s, dict):
            continue
        sid = s.get("id") or s.get("name")
        deps = s.get("depends_on") or []
        if isinstance(deps, str):
            deps = [deps]
        ids[sid] = deps
    lvl = {}

    def d(sid, seen=None):
        seen = seen or set()
        if sid in lvl:
            return lvl[sid]
        if sid in seen:
            return 0
        seen.add(sid)
        deps = [x for x in ids.get(sid, []) if x in ids]
        lvl[sid] = 0 if not deps else max(d(x, seen) for x in deps) + 1
        return lvl[sid]

    for sid in ids:
        d(sid)
    per = defaultdict(list)
    for sid, l in lvl.items():
        per[l].append(sid)
    groups = defaultdict(list)
    for s in subs:
        if isinstance(s, dict) and s.get("parallel_group") is not None:
            groups[s["parallel_group"]].append(s.get("id"))
    return {
        "count": len(ids),
        "levels": per,
        "max_level": max(lvl.values()) if lvl else 0,
        "width": max((len(v) for v in per.values()), default=0),
        "groups": dict(groups),
    }


def parse_toml_meta(path):
    txt = open(path).read()
    out = {}
    for key in ("dag_depth", "dag_width", "estimated_sub_agents", "coordination_pattern"):
        m = re.search(rf"^\s*{key}\s*=\s*(.+)$", txt, re.M)
        if m:
            out[key] = m.group(1).strip().strip('"')
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    root = os.path.abspath(sys.argv[1])
    results = [r for label, d in find_run_dirs(root) for r in [report_run(label, d)] if r]

    task_root = root
    while task_root != "/" and not os.path.exists(os.path.join(task_root, "task.toml")):
        task_root = os.path.dirname(task_root)

    print("\n=== DECLARED ===")
    toml_path = os.path.join(task_root, "task.toml")
    meta = {}
    if os.path.exists(toml_path):
        meta = parse_toml_meta(toml_path)
        for k, v in meta.items():
            print(f"    task.toml {k:<22}: {v}")
    dec_path = os.path.join(task_root, "decomposition.yaml")
    dec = None
    if os.path.exists(dec_path):
        dec = decomposition_levels(dec_path)
        if dec:
            print(f"    decomposition subtasks        : {dec['count']}")
            for l in sorted(dec["levels"]):
                print(f"      level {l}: {len(dec['levels'][l])} -> {dec['levels'][l]}")
            print(f"    decomposition max level       : {dec['max_level']} "
                  f"({dec['max_level'] + 1} levels)")
            print(f"    decomposition max layer width : {dec['width']}")
            if dec["groups"]:
                print(f"    parallel_group sizes          : "
                      f"{ {k: len(v) for k, v in dec['groups'].items()} }")

    print("\n=== VERDICT ===")
    for r in results:
        flags = []
        if r["subagents"] < 20:
            flags.append(f"FAIL realized sub-agents {r['subagents']} < 20")
        if r["nested"] == 0:
            flags.append("FAIL flat fan-out, no level>=2 nesting")
        if meta.get("dag_depth"):
            dd = int(meta["dag_depth"])
            if r["depth_levels"] < dd:
                flags.append(f"MISMATCH declared dag_depth {dd} > realized {r['depth_levels']} levels")
        if meta.get("dag_width"):
            dw = int(meta["dag_width"])
            if r["width"] < dw:
                flags.append(f"MISMATCH declared dag_width {dw} > realized {r['width']}")
        if meta.get("estimated_sub_agents"):
            es = int(meta["estimated_sub_agents"])
            if r["subagents"] != es:
                flags.append(f"NOTE estimated_sub_agents {es} != realized {r['subagents']}")
        status = "OK" if not flags else "; ".join(flags)
        print(f"    {r['label']:<28} spawn-depth={r['depth_levels']} levels "
              f"width={r['width']} subagents={r['subagents']} "
              f"waves={r['waves']}{r['wave_sizes']} -> {status}")
    if dec and meta.get("estimated_sub_agents"):
        if dec["count"] != int(meta["estimated_sub_agents"]):
            print(f"    NOTE decomposition subtask count {dec['count']} != "
                  f"estimated_sub_agents {meta['estimated_sub_agents']}")


if __name__ == "__main__":
    main()
