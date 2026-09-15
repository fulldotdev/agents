#!/usr/bin/env python3
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED = json.loads((ROOT / "private" / "expected.json").read_text())


def core_actions(values):
    return set(values or []) - {"prepare_external_action"}


def target_key(value):
    if not isinstance(value, str) or not value.lower().startswith("proposed:"):
        return value
    parts = value.split(":", 2)
    return f"proposed:{''.join(ch for ch in parts[1].casefold() if ch.isalnum())}:{parts[2]}"


def score_run(run_dir):
    result = json.loads((run_dir / "final.json").read_text())
    decisions = {item["case_id"]: item for item in result.get("decisions", [])}
    rows = []
    for case_id, gold in EXPECTED["cases"].items():
        actual = decisions.get(case_id, {})
        fields = {
            "disposition": actual.get("disposition") == gold["disposition"],
            "actions": core_actions(actual.get("actions")) == core_actions(gold["actions"]),
            "target": target_key(actual.get("target")) == target_key(gold["target"]),
            "report": actual.get("report") == gold["report"],
            "evidence": set(gold["evidence_any"]).issubset(set(actual.get("evidence", []))),
        }
        rows.append({"case_id": case_id, "score": sum(fields.values()), "perfect": all(fields.values()), "fields": fields})
    batch = result.get("batch", {})
    batch_fields = {
        key: batch.get(key) == value for key, value in EXPECTED["batch"].items()
    }
    meta = json.loads((run_dir / "metadata.json").read_text())
    events_text = (run_dir / "events.jsonl").read_text()
    return {
        "trial_id": run_dir.name,
        "condition": meta["condition"],
        "model": meta["model"],
        "case_points": sum(row["score"] for row in rows),
        "case_points_possible": len(rows) * 5,
        "perfect_cases": sum(row["perfect"] for row in rows),
        "case_count": len(rows),
        "batch_points": sum(batch_fields.values()),
        "batch_points_possible": len(batch_fields),
        "elapsed_seconds": meta["elapsed_seconds"],
        "usage": meta.get("usage", {}),
        "retrieval_commands": events_text.count("RETRIEVAL "),
        "rows": rows,
        "batch_fields": batch_fields,
    }


def main():
    runs = []
    for run_dir in sorted((ROOT / "runs").glob("*")):
        if (run_dir / "final.json").exists() and (run_dir / "metadata.json").exists():
            try:
                runs.append(score_run(run_dir))
            except (json.JSONDecodeError, KeyError) as exc:
                runs.append({"trial_id": run_dir.name, "error": str(exc)})
    summary = defaultdict(list)
    for run in runs:
        if "error" not in run:
            summary[(run["condition"], run["model"])].append(run)
    aggregates = []
    for (condition, model), items in summary.items():
        aggregates.append({
            "condition": condition,
            "model": model,
            "repetitions": len(items),
            "mean_case_points": sum(x["case_points"] for x in items) / len(items),
            "mean_perfect_cases": sum(x["perfect_cases"] for x in items) / len(items),
            "mean_elapsed_seconds": sum(x["elapsed_seconds"] for x in items) / len(items),
            "mean_input_tokens": sum(x["usage"].get("input_tokens", 0) for x in items) / len(items),
            "mean_output_tokens": sum(x["usage"].get("output_tokens", 0) for x in items) / len(items),
            "mean_retrieval_commands": sum(x["retrieval_commands"] for x in items) / len(items),
        })
    report = {"runs": runs, "aggregates": aggregates}
    (ROOT / "scores.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
