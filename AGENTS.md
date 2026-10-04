<!-- AI-Native SDLC Router -->
## SDLC Workspace
- Read `_system/SDLC.md` for setup, evidence boundaries, and recovery.
- Inspect `python3 _system/scripts/sdlc.py status` before creating a run.
- Read `stages/<stage-name>/CONTEXT.md` before processing a stage.
- Keep factory references in `_shared/` unchanged during feature runs.
- Use separate worktrees or clones for code-writing runs.
- Stage skills: see the Skills section of the current stage's CONTEXT.md.
- Need a specialised skill mid-task? `tink-route --receipt runs/<slug>/skills.jsonl "<what you need>"` prints it on stdout; exit 1 means none fits, so continue without one.
<!-- End AI-Native SDLC Router -->

<!-- tink:rules begin skillset=deployment-skillset digest=dbf7e19cffa4cf6e99841c1fd2652e8002ed44fe76b7d425a8bcfe0d925fce5f -->
Discipline rules for this phase (compiled by tink; do not edit by hand):
- principle-prove-it-works: Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.' (full: .tink/.active/principle-prove-it-works/SKILL.md; run: tink mount principle-prove-it-works)
<!-- tink:rules end -->
