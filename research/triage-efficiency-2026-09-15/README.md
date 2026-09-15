# Triage efficiency benchmark

This benchmark compares triage quality and context cost across three conditions:

1. Current full-context interface with `gpt-5.6-sol`, high reasoning.
2. Compact retrieval interface with `gpt-5.6-sol`, high reasoning.
3. Compact retrieval interface with `gpt-5.6-terra`, high reasoning.

Each condition runs twice with the same 16 synthetic cases. The expected outcomes are frozen before model trials and are never copied into a trial directory. Trials use read-only Codex sandboxes, no connectors, no network work, and no live APIs or actions.

The compact condition starts from a complete concise index and may retrieve the same full evidence available to the full-context condition through local `triage show` and `triage context` commands. A decision that needs details must cite the retrieved source or destination locator.

## Files

- `fixtures/evidence.json`: synthetic source and destination records.
- `fixtures/compact-index.json`: concise complete index shown initially in compact trials.
- `model/output-schema.json`: required structured response.
- `private/expected.json`: hidden scoring key.
- `run_benchmark.py`: stages isolated trial directories and runs Codex.
- `score_benchmark.py`: deterministic scorer.
- `baseline-snapshot.json`: immutable Git commit used for the old-interface instruction packet.

## Reproduce

Prepare only:

```bash
python3 run_benchmark.py --prepare
```

Run all six trials after the compact interface snapshot is recorded:

```bash
python3 run_benchmark.py --run-all
python3 score_benchmark.py
```

The runner stores the exact staged inputs, command metadata, JSONL event stream, final response, stderr, elapsed time, and parsed usage under `runs/`.

## Limits

This tests reasoning over realistic synthetic snapshots and local retrieval. It does not test the latency, authentication, pagination, or failure behavior of live Gmail, Slack, WhatsApp, Notion, Calendar, or T3 services.
