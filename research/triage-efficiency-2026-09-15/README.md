# Triage efficiency benchmark

This benchmark compares triage quality and context cost across four conditions:

1. Current full-context interface with `gpt-5.6-sol`, high reasoning.
2. Compact retrieval interface with `gpt-5.6-sol`, high reasoning.
3. Compact retrieval interface with `gpt-5.6-terra`, high reasoning.
4. Current full-context interface with `gpt-5.6-terra`, high reasoning.

Each condition runs twice with the same 16 synthetic cases. The expected outcomes are frozen before model trials and are never copied into a trial directory. Trials use read-only Codex sandboxes, no connectors, no network work, and no live APIs or actions.

The compact condition starts from a complete concise index and may retrieve the same full evidence available to the full-context condition through local `triage show` and `triage context` commands. A decision that needs details must cite the retrieved source or destination locator.

The deterministic score treats `prepare_external_action` as ledger bookkeeping rather than a case action and normalizes the casing and separators of proposed target types. It still requires the exact disposition, core actions, existing target, report behavior and evidence locators.

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

Run all eight trials after the compact interface snapshot is recorded:

```bash
python3 run_benchmark.py --run-all
python3 score_benchmark.py
```

## Results

| Interface | Model | Mean score | Mean input | Mean output | Mean time |
| --- | --- | ---: | ---: | ---: | ---: |
| Full | Sol | 69 / 80 | 179,854 | 8,673 | 187 s |
| Compact | Sol | 67 / 80 | 339,435 | 10,021 | 240 s |
| Full | Terra | 66.5 / 80 | 147,788 | 9,091 | 172 s |
| Compact | Terra | 63.5 / 80 | 196,257 | 7,510 | 157 s |

All eight runs got both batch-level checkpoint decisions right. Every full-context Sol and Terra run also got all 16 dispositions and all core actions right. Compact retrieval was less reliable at returning exact targets and evidence locators and used 89% more input with Sol in this dense batch because each run made 24 to 39 retrieval calls. Full-context Terra used 18% less input than Sol but 5% more output, scored 2.5 points lower and returned fewer exact targets. Evidence citation varied sharply for both models. Live actionable triage therefore keeps full-context Sol until real runs show that Terra preserves quality. The scheduler wrapper still skips proven-empty batches before starting a model.

The runner stores the exact staged inputs, command metadata, JSONL event stream, final response, stderr, elapsed time, and parsed usage under `runs/`.

## Limits

This tests reasoning over realistic synthetic snapshots and local retrieval. It does not test the latency, authentication, pagination, or failure behavior of live Gmail, Slack, WhatsApp, Notion, Calendar, or T3 services.
