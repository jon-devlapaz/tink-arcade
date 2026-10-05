# Seed: solo Galaga-style game
Date: 2026-10-04. Status: Jon approved the combined implementation brief and checklist. The runtime records the decision.

## Goal
Jon asked to add a Galaga-style game to tink-arcade from start to finish as a real tink-substrate trial. His clarification was: "solo first. the goal is to find the best path for tink-substrate and document issues".

## Agreed direction
A solo terminal shooter with enemy formations, diving attacks, shooting, lives, score, and increasingly difficult waves. This follows the proposed slice and Jon's solo-first choice. Deliver a tested PR; preserve the separate Tetris-versus-Jev PR.

## Working defaults
Use Python's standard library and curses, original text graphics, offline play, three lives, seeded repeatable runs, pause, restart, quit, and a resize pause. No Jev calls, multiplayer, copied game assets, persistent scores, or arcade-ROM emulation. These defaults are included in the approved brief.

## What this trial should teach
Can the saved work record and actual source state carry a hunch through development and PR delivery without the human repeating context? Record confusing status, stale intent, manual coordination, setup costs, and approval friction in tink-substrate. Distinguish observed problems from suggestions.

## Risks and probes
Pre-mortem: tests can pass while the shooter feels poor. Exercise the real terminal; leave enjoyment for Jon to judge.
Counterexample: a minimized terminal must not consume lives. Pause simulation until size is restored.
Outside view: enemies and bullets must remain consistent across frame rates and long pauses. Use a fixed simulation step and deterministic tests.
Not assessed: human enjoyment, other terminals beyond tested environments, and multi-project or agent ownership integrations.

## Evidence
The existing repository is a Python curses Tetris game. Main is c83dd829aa47c1b4e8baf2f3833327e6cfd77e7a. Tetris-versus-Jev remains open as PR 1. Neither existing game nor PR is replaced by this work.

## Next
Complete implementation review, verify the committed candidate, compare the shared dashboard with live sources, and deliver a PR. The seed records intent; workflow status and test receipts record implementation evidence.
