# Notebook sync report (2026-11-27 21:49)

## Self-fixes

- None yet.

## Evolved agent prompts

- **publisher** is at v3 (the seed in Cell 19 is only used on a fresh install)
  - v1 replaced 2026-11-26T14:43: Publisher had failures due to hitting the daily repository creation limit. Updated prompt to handle the daily limit gracefully.
  - v2 replaced 2026-11-26T23:21: F7: experiments go to one projects repo, no daily limit
  ```diff
  --- before
  +++ after
  @@ -1 +1 @@
  -You are the Publisher. Call publish_experiment(slug) for the slug in CONTEXT and report the result. If publish_experiment fails because the daily limit of new repositories has been reached, gracefully acknowledge the limit, report that it will retry tomorrow, and do not treat it as an unrecoverable failure.
  +You are the Publisher. Call publish_experiment(slug) for the slug in CONTEXT: it puts the experiment in its own folder of the private projects repo, with no daily limit, and returns the folder link. Then check list_experiments: if a project there has passed tests, uses 2 or more skills and all its milestones are done, call graduate_project(slug) once (1 a day; a 'limit reached' reply is fine). Report what you published.
  ```

## Learned score weights

- Defaults in use.

## Active rules

- (write_tool) Validate Mermaid syntax and class definition formats against unit test assertions before running tests.
- (write_tool) Verify existing test assertions for Mermaid syntax formatting before modifying the diagram generator implementation.

## GitHub engine vs this notebook

- Cell 42: 6 line(s) on GitHub vs 28 in the notebook; you edited this cell (will be exported)
  ```diff
  -            "heal_log": {i.get("function"): [f"{x.get('result')}: {str(x.get('detail', ''))[:240]}" for x in i.get("heal_log", [])][-2:]
  -                         for i in issues.values() if i.get("function") in ("drill_open_count", "drill_skill_names")}}
  +            "heal_log": {f: [f"{x.get('result')}: {str(x.get('detail', ''))[:240]}" for i in issues.values()
  +                             if i.get("function") == f for x in i.get("heal_log", [])][-3:]
  +                         for f in ("drill_open_count", "drill_skill_names")}}
  + DRILL_ATTEMPTS_PER_MONTH = 3
  + 
  ```

## After the export

- IDENTICAL
