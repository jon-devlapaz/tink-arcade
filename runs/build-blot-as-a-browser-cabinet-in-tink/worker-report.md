# Blot build handoff

Implemented the approved standalone browser cabinet in `blot/`, with root `tinkery.preview`. No terminal-menu integration changed. The game uses local HTML, CSS and JavaScript, the Socratink paper/ink/jade palette, keyboard and pointer steering, six collectible words, growth and slowdown after every new word, a 40-second active-play drying clock, completion, pause and restart. Blur and hidden-tab transitions pause play.

## Inputs and authority

Read checkout `AGENTS.md`, `_system/SDLC.md`, stage-3 context, the supplied build step contract, the run brief, confirmed seed and locked seed checks. The brief remains an empty template; the seed supplies the scope. Stage-3 status reported approved and matching the confirmed seed. Implementation authority was the current user's build instruction, not the seed's agent confirmation.

Seed SHA-256: `4594775f3a5b8f7785922ec9c7f7d43186d485acb93d473ee16650b8f6d4a16a`. Run ID: `c3601c68-76a0-4998-8f4b-70421f9b4586`. The step contract and model/thinking pin were not changed. No stage, step, decide, mark, commit, stage-to-index or push command was run.

## Interfaces

- `blot/index.html` is the player entry point. `tinkery.preview` supplies the approved localhost static-server command, using `blot` as its directory.
- `window.Blot`, its constructor and `advance(seconds, dx, dy)` isolate simulation from rendering. This is the only added game-code public interface. It owns contact, normalized movement, growth, speed and drying. The UI remains private in an immediately invoked function.
- `tests/run_blot_browser.cjs` is the dependency-free browser execution bridge. Python unittest launches it with Node.js and a Chromium executable. It uses Chromium's debugging pipe, observes actual page requests, runs the real page and rejects external resource requests. `BLOT_CHROME` can name the installed browser. No packages were installed.
- `scripts/check_blot_mutations.py` reruns isolated targeted reversions inside disposable checkout-local copies. `tests/__init__.py` makes the seed's direct unittest path invocation resolve this repository's tests.

## Checks

- `python3 -B scripts/check_all.py`: passed. 574 tests, five existing opt-in/platform skips, and all 12 terminal cabinets passed. Evidence: `runs/build-blot-as-a-browser-cabinet-in-tink/build-check-all.log`.
- Both seed-proposed Blot unittest commands passed, with two discoverable tests. Assertions execute actual JavaScript in installed Google Chrome, including keyboard-driven rendered movement, paused versus active UI time, contact, successive growth/slowdown, completion and drying failure.
- `python3 -B scripts/check_blot_mutations.py`: passed. Separate growth, slowdown, contact and drying reversions each failed the intended assertion.
- `node --check` passed for the game, UI, browser assertions and execution bridge. No separate project lint or type-check command is configured.
- `git diff --exit-code -- play arcade_menu scripts/check_arcade.py`: passed, unchanged launch behavior.
- `sdlc.py verify`: ran the configured checks and activated seed commands green. Receipt `04-test/output/verification.json` reports seed-1 through seed-4 proven, seed-5 pending, and `result: awaiting-attestation`. It exited 1 for missing seed-5, so overall verification is not passing.

Added only activation objects for seed-1, seed-2 and seed-4, preserving original proposals verbatim, including the proposed trailing newlines. Commands and working directories match their confirmed proposals. Status recognizes all three as activated as confirmed.

An initial Chromium `--dump-dom` experiment failed during browser teardown and exposed the CSP's intentional prohibition of eval. The retained bridge instead uses the native debugging pipe, accesses the explicit game interface without eval, terminates its browser, and has process-group cleanup on timeout. Final browser assertions pass. No local server was started. Process inspection at handoff found no retained Blot browser/bridge process. No production/live endpoint requests were sent; browser checks use checkout-local file URLs and prohibit external page requests.

## Open judgment

A person still must play through Taste v and judge readability and enjoyment. `taste` was not found on PATH; its executable and invocation remain unestablished. No human verdict, attestation or release acceptance was fabricated. Timing and word layout are builder tuning, not human-accepted quality. Establish Taste v, collect the actual person's observation, record it through the authorized workflow, and rerun verification. Changes remain uncommitted because no commit was authorized.

No unreadable named implementation input was substituted. The referenced external Socratink design document was not needed or read; the approved checkout `DESIGN.md` supplied the palette. Taste v remains the unavailable named capability.

## Skills

`principle-build-the-lever` changed verification into reusable browser and targeted-mutation runners rather than manual inspection. `unslop` kept player instructions and this report literal and distinguished machine proof from the outstanding human judgment.
