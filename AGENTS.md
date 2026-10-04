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

<!-- tink:rules begin skillset=build-skillset digest=7c693535576993412cc58f383c37322d844d6e20a29a781c170fe28446ec7b15 -->
Discipline rules for this phase (compiled by tink; do not edit by hand):
- principle-build-the-lever: Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun. (full: .tink/.active/principle-build-the-lever/SKILL.md; run: tink mount principle-build-the-lever)
- unslop: Cut AI tells from any writing. Must always apply. (full: .tink/.active/unslop/SKILL.md; run: tink mount unslop)
<!-- tink:rules end -->
