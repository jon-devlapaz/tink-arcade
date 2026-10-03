# Socratink / Paper Tetris

> Make room for the next idea.

## Design intent

**A quiet paper workspace with the response of a mechanical keyboard.** The board should feel considered and readable, not like a neon arcade cabinet. The game is quick; the interface is calm.

This document describes the current terminal app and the rules for evolving it. It adapts the [Socratink design language](../socratink/DESIGN.md), not the web app's components or typography.

### Principles

- **The board comes first.** Decoration must never obscure a piece, its landing position, or the next decision.
- **Paper, ink, one accent.** Warm paper is the ground; carbon ink is settled information; jade marks active play and important controls.
- **Quiet visuals, crisp feedback.** Sound is short mechanical clicks and clacks, not paper rustling. The paper metaphor is visual.
- **Immediate entry and exit.** Launch straight into play. Keep controls visible. Quit cleanly without changing the user's terminal settings.
- **Graceful degradation.** The game remains playable without color or sound and freezes safely when the terminal is too small.

## Visual system

### Palette

The renderer uses indexed terminal colors rather than true-color brand values. The RGB approximations below assume the standard xterm palette; terminals can customize their palettes.

| Role | Socratink reference | 256-color index / approximation | Use |
| --- | --- | --- | --- |
| Paper | `#fffcf0` | `230` / `#ffffd7` | Canvas and panel ground |
| Carbon ink | `#100f0f` | `233` / `#121212` | Primary text, settled blocks, previews |
| Jade | `#1f7a72` | `29` / `#00875f` | Active piece, clear flash, important control hints |
| Graphite | `#575653` | `240` / `#585858` | Metadata, empty grid, pencil ghost |
| Rules | Subtle ink dividers | `245` / `#8a8a8a` | Panel outlines |

On an eight-color terminal, use white paper, black ink, and cyan as the accent approximation. Graphite and rules collapse to black. Color setup requires at least five color pairs; otherwise retain attribute-based rendering. `--no-color` skips color initialization and uses the terminal's existing foreground/background.

Do not color each tetromino differently. Position, silhouette, and state carry the information; jade is not a decorative rainbow substitute.

### Type and marks

The terminal owns the font and its size. Use its monospace grid, ASCII, spacing, bold, dim, and reverse-video attributes. Do not require a custom font, Nerd Font icons, emoji, or Unicode box-drawing widths.

| Mark | Meaning | Treatment |
| --- | --- | --- |
| `[]` | Active block | Jade, bold, reverse video |
| `[]` | Settled or preview block | Carbon ink, reverse video |
| `()` | Ghost landing position | Graphite, dim, no reverse video |
| ` .` | Empty board cell | Graphite |
| `+`, `-`, `\|` | Panel boundary | Rule color; dim in monochrome |
| `=` | Cleared-row feedback | Brief jade reverse-video flash |

Each board cell occupies **two character columns and one row**. The ghost and active piece must remain distinguishable in monochrome. Uppercase labels organize the panels; short sentence-case messages provide a quieter secondary voice.

Paper texture is implied by the background and restraint, not by visual noise. Do not port the website's serif display type, grain overlays, gradients, or ink-orb animation into the terminal.

## Layout

The interface is a fixed **80-column by 30-row canvas**, centered in larger terminals. The playfield is **10 cells wide by 20 cells high**. Increasing terminal size adds margins; it does not change the game geometry.

Structural sketch, not a cell-exact rendering:

```text
                  . socratink / paper tetris
                  make room for the next idea.

   + HOLD / MARGIN +   + PLAY / PAPER +   + NEXT / 7-BAG +
   | Held piece    |   |              |   | 01           |
   | C / LOCKED    |   |              |   | 02           |
   +---------------+   |  10 x 20     |   | 03           |
                       |  playfield   |   +--------------+
   + SESSION ------+   |              |
   | SCORE         |   |              |   Brief feedback
   | LEVEL         |   |              |   Sound status [M]
   | LINES         |   |              |   () pencil / ghost
   | SESSION BEST  |   |              |
   +---------------+   +--------------+

   Movement / rotation controls
   Drop / hold / pause / restart / mute / quit
```

- **Left margin:** one held piece, hold availability, and session statistics.
- **Center:** the board, with the ghost behind the active piece.
- **Right margin:** the next three pieces, transient feedback, sound state, and ghost legend.
- **Bottom:** two persistent rows of keyboard help, not a hidden help modal.
- **Overlays:** pause and game over occupy the center of the board. Keep the surrounding statistics and previews in place.

Panel boundaries are light separators, not heavy containers. Keep whitespace between columns without pushing essential information below the minimum canvas.

## Interaction and game rhythm

The game begins immediately; there is no title-screen confirmation or menu to dismiss. Use a fair seven-bag piece sequence, a landing ghost, and one hold per placed piece. Rotation supports wall/floor kicks. Hard drop commits immediately.

The current lock delay is **450 ms**, with at most **15 movement/rotation resets** per piece. These limits must not be bypassed by repeatedly lifting a piece off the floor. Advance one level per ten cleared lines. Session best survives `R` restarts but is not saved after exit.

### Controls

Letter bindings accept either case.

| Action | Keys |
| --- | --- |
| Move left / right | Left / Right arrows or `A` / `D` |
| Soft drop | Down arrow or `S` |
| Rotate clockwise | Up arrow or `X` |
| Rotate counterclockwise | `Z` |
| Hard drop | Space |
| Hold / swap | `C` |
| Pause / resume | `P` |
| Restart | `R` |
| Mute / unmute | `M` |
| Quit | `Q` or Ctrl-C |

Target a 60 Hz update/render loop, not a guaranteed display refresh rate. Read bounded input batches so held keys cannot starve drawing. Do not add blocking animations, transition screens, or decorative delays to gameplay.

### States and copy

Keep messages brief and useful. The paper vocabulary belongs in secondary feedback; labels such as `SCORE`, `PAUSED`, and `GAME OVER` remain explicit.

| State | Current message / behavior |
| --- | --- |
| Start / restart | `A fresh page.` |
| Single clear | `One line, distilled.` |
| Double clear | `Two lines, distilled.` |
| Triple clear | `Three lines, distilled.` |
| Four-line clear | `A clean slate. +4` |
| Pause | `PAUSED` / `Take a breath.`; freeze gameplay |
| Game over | `GAME OVER` / `Turn a fresh page.`; offer restart and quit |
| Small terminal | `Resize terminal to at least 80 x 30.`; show current size and freeze simulation |

Line clears use a **180 ms** row flash and a short message; there is no full-screen celebration. Pausing freezes game timers. On resize recovery, discard elapsed catch-up time and preserve any pre-existing pause state. While undersized, ignore gameplay inputs but keep mute and quit available.

Restart and mute remain usable on pause/game-over overlays at a playable terminal size. `R` resets the game; it does not reload code or sound assets from disk.

## Sound design

**Modern mechanical keyboard feedback is the chosen direction.** The earlier synthesized paper sounds are not the current design. Avoid rustles, sweeps, ambient loops, music, and long reverberant tails.

| Event | Sound | Bundled file |
| --- | --- | --- |
| Successful movement / soft drop | Small tactile click | `tactile.wav` |
| Successful rotation | Clicky Cherry MX Blue tap | `mx-blue.wav` |
| Hold, pause/resume, restart, unmute | The same short MX Blue tap | `mx-blue.wav` |
| Placement / hard drop, game over | Enter-key clack | `enter.wav` |
| Line clear | Short paired click-clack | `clear.wav` |

The three chosen recordings are by **StavSounds**, **Professor-Syntax**, and **alpinemesh**; the clear cue combines the latter two clips. They are bundled as short 44.1 kHz mono 16-bit PCM WAVs under CC0. Source links, transformations, and hashes live in [the sound credits](neon_tetris/sounds/credits.json). Playback requires no network access.

### Feedback rules

- Sound confirms successful actions, not every keypress. Blocked movement, ineffective rotation, and paused gameplay controls stay silent. Ordinary falling is silent; placement, line clears, and game-over transitions receive feedback.
- Select at most one cue per input/render batch: **clear > game over > placement > rotation/switch > movement**. Equal-priority cues keep the latest request.
- Expire pending cues older than **150 ms**. Never let key repeat build a delayed queue of clicks.
- Sound starts enabled. `M` stops active/pending cues when muting; unmuting gives one short confirmation. `--no-sound` disables audio setup for the whole run and cannot be overridden with `M`.
- Keep sound state visible: `key sound on [M]`, `key sound muted [M]`, `key sound off`, or `key sound unavailable`.
- Audio failure must not prevent play. Show the unavailable state and report the warning after returning from the normal game loop.

### Playback contract

On macOS, preload the four samples in memory using `AVAudioPlayer`, with **two reusable voices per sample**. Do not spawn a player process for each click. If both voices for a sample are occupied, reuse the oldest rather than adding voices or waiting for its tail.

**Service macOS completion events every frame with a non-blocking CoreFoundation run-loop poll.** Curses does not provide a Cocoa event loop. Omitting this can make later `play()` calls report success while producing silence. A successful call alone is not an audio acceptance test: verify playback advancement and nonzero sample levels across repeated plays, then listen for quality on the intended output device.

The non-macOS fallback uses `paplay` or `aplay`, with one child at a time and the same stale-cue limit. It is not the native preloaded path and should not be advertised as having identical latency. Release audio resources on quit, Ctrl-C, and exceptions.

## Accessibility and terminal behavior

- Never encode essential state in color or audio alone. Preserve shapes, text labels, and attribute differences.
- Support `--no-color` and `--no-sound` independently.
- Keep input keyboard-only and controls visible. Do not require a mouse or terminal-specific escape-key shortcuts.
- Clip safely during resize, including at the lower-right terminal cell. A small window is a recoverable state, not a crash.
- Restore terminal modes and cursor behavior on exit. Do not leave audio playing after the app closes.
- Font size, palette overrides, and rendering of dim/bold attributes remain the terminal user's choices. The app has no built-in dark theme; monochrome can use the user's dark terminal palette.

## Implementation boundaries

| File | Responsibility |
| --- | --- |
| [engine.py](neon_tetris/engine.py) | Rules, piece sequence, scoring, collision, timing; independent of the terminal and audio |
| [ui.py](neon_tetris/ui.py) | Palette, layout, copy, controls, resize behavior, mapping game changes to sound cues |
| [audio.py](neon_tetris/audio.py) | Cue mapping, priority, expiry, mute, fallback process playback |
| [_mac_audio.py](neon_tetris/_mac_audio.py) | Native sample ownership, voice reuse, completion-event processing, cleanup |
| [__main__.py](neon_tetris/__main__.py) | CLI options, terminal checks, startup and exit handling |
| [sounds/](neon_tetris/sounds/) | Local recordings and provenance |

The directory and Python package retain the legacy names `neon-tetris` and `neon_tetris`; these are implementation identifiers, not the visual identity.

On the configured machine, launch from any directory with `socratink-tetris`. That user-local launcher points to this checkout; it is not a portable installer. The checkout-local entry point is `python3 -m neon_tetris`. Both support `--seed INT`, `--no-color`, and `--no-sound`.

## Change checklist

Before accepting an interface or feedback change:

- Check the board, ghost, previews, and controls at exactly 80 x 30 and in a larger window.
- Check 256-color, basic-color, and monochrome rendering without changing game geometry.
- Exercise pause, game over, small-window recovery, mute, and quit; preserve both gameplay and terminal state.
- For audio changes, test first playback, spaced repeats, rapid repeats, mute/resume, and cleanup. Include native rendered-signal checks, not just mocks or subprocess creation counts.
- Keep tests for game rules separate from presentation tests. A visual redesign must not quietly alter scoring, lock timing, or fairness.
- Preserve licensed sample provenance when replacing or processing recordings.

From this directory, run the normal suite with `python3 -m unittest discover -s tests`. For audio changes on macOS, also run `NEON_TETRIS_AUDIO_TESTS=1 python3 -m unittest discover -s tests`; this opt-in suite plays and meters real samples.

There is currently no persistent leaderboard, mouse interface, multiplayer mode, music, or theme selector. Do not introduce these as incidental parts of a visual cleanup. Keep the defining contrast: **calm paper, crisp keys, uninterrupted play.**
