# Tink arcade

Terminal games for a person and an AI opponent. The first game is paper Tetris,
with the existing solo game and a live race against Jev.

## Play

Use Python 3.11 or newer on macOS or Linux and a terminal at least 80 columns by
30 rows. The game uses Python's standard library. No package installation is needed.

```sh
python3 -m neon_tetris
python3 -m neon_tetris --versus-jev --seed 1
```

Versus mode requires `TYPESAFE_API_KEY` in your environment. Set it through your
usual secret manager or shell setup; never put it in source control. Solo mode
works offline. Add `--no-sound` or `--no-color` if desired.

Both players receive the same sequence of pieces. First to clear 20 lines wins;
topping out loses. A simultaneous finish in the same update is a draw. Jev's
thinking time counts as play time. There is no artificial speed adjustment.

| Key | Action |
| --- | --- |
| Left/right or A/D | Move |
| Down or S | Soft drop |
| Up or X / Z | Rotate clockwise / counterclockwise |
| Space | Hard drop |
| C | Hold |
| P | Pause both boards |
| R | Restart both boards with the same seed |
| Enter | Retry after a Jev error |
| M | Toggle sound |
| Q or Ctrl-C | Quit |

A failed Jev request pauses both boards and shows an error. Retry is explicit.
An undersized terminal freezes both boards until it is large enough. Restarted
matches ignore earlier replies, but their reported usage still counts toward cost.

## Jev and cost

The opponent uses the TypeSafe API with the pinned `jev-1.13.0` model. Jev receives
only game state and legal moves. The app enumerates placements and describes their
results; Jev selects a move. There is no scripted fallback opponent.

The game displays estimated USD for the current app session, including rematches.
The estimate uses reported input tokens and the published rate of $0.042 per million
input tokens, with free output, checked on 2026-10-03. See the
[official model pricing](https://docs.typesafe.ai/models.md).
Prices may change; update the price table when adopting a new price or model.

There is no spending cap. Unknown usage or model pricing displays `+ unknown`;
an in-flight request displays `+ pending`. The final line after quitting includes
that uncertainty. Exiting does not guarantee cancellation of an already sent
request. Estimates are not invoice totals.

Opponent strength and pacing need human playtesting. Automated correctness checks
cannot tell us whether this is a good race.

## Check the game

```sh
python3 -B -m unittest discover -s tests
python3 -B scripts/check_terminal.py
# Calls real Jev and incurs usage:
python3 -B scripts/check_terminal.py --live
```

The terminal script exercises the actual curses program in a pseudo-terminal,
including input, pause, resize, restart, and exit. Native-audio integration tests
are opt-in; their skips are reported. Sound sample credits and CC0 provenance are
in `neon_tetris/sounds/credits.json`.

## Work in progress

This feature is the first hunch-to-PR trial for tink-substrate. Current work and
remaining checks are in [the handoff](runs/play-against-jev/handoff.md).
The [build brief](runs/play-against-jev/brief.md) records the reviewed proposal;
its historical statements are not live status. Query current workflow evidence with:

```sh
python3 _system/scripts/sdlc.py status play-against-jev
```

The original solo design is recorded in [DESIGN.md](DESIGN.md).

The installed workflow files in `_system`, `_shared`, `stages`, and the skillset
pins come from [tink-sdlc](https://github.com/jon-devlapaz/tink-sdlc), scaffold
1.19.0. Its [MIT notice](licenses/tink-sdlc-MIT.txt) applies to those files.
