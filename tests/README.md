# Swings AI tests

`python tests/run_tests.py` runs the 10 suites (about 40 s); `--full` adds the 6-run simulated regression (about 3 min).
Each suite runs on a throwaway copy of this repo with no tokens and a scripted stand-in for Gemini, so tests never
touch GitHub, Gemini or the live state.

| Suite | What it proves |
|---|---|
| lc_test | Long-term coherence: decision ledger, consistency guard, charter, monthly plan, invariants |
| f6_test, f6_tamper | Need-driven scouting closes gaps, and rewritten acceptance tests are caught |
| f7_test | Experiments become folders in one projects repo; graduation rules |
| pub_direct_test | The publisher runs with no LLM call |
| f8_test | Real projects: proposal checks, one milestone per run, skills counted from imports |
| f9_test | Sustainability meters: Gemini quotas, GitHub reserves, weekly report, pruning |
| f10_test | Notebook sync: sync report, fix states, drift guard, IDENTICAL check |
| p5q_test | Phase 5 quality: tools graded on real repo inputs, repairs, usefulness and language in scouting |
| p5_test | Phase 5: experiments built on skill tools, the end-of-run work pass, useful runs, the CI result in the report |

CI: `.github/workflows/tests.yml` (written by notebook Cell 15) runs `--full` on every engine or test change, daily,
and on demand. Cell 15 runs the quick suites on the candidate engine before every export.
