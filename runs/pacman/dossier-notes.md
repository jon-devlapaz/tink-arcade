# Dossier read, start of slice 2

Source: the Pac-Man Dossier at https://pacman.holenet.info/, read as page text (88,078 characters, fetched 2026-10-06) instead of through a model summary. These are my notes in my own words, with the numbers. Nothing here is quoted.

## Where the page differs from the two fetch summaries or from the approved brief

| # | Topic | Fetch summary / brief said | Page says | What slice 2 does |
|---|---|---|---|---|
| 1 | Wave timers by level | Level 1 table used for every level (brief: stated simplification) | Level 1: 7/20/7/20/5/20/5/chase. Levels 2-4: 7/20/7/20/5/**1033**/**1/60 s**/chase. Levels 5+: **5/20/5/20/5/1037**/1/60 s/chase | Keep the approved brief (level-1 table every level). The schedule is one function, so the faithful table is a data edit. **Needs Jon's call.** |
| 2 | How a ghost picks a turn | "Takes the exit nearest its target" | It decides one tile early. On reaching the tile before an intersection it looks at the tiles one step beyond the intersection and picks the nearest to its target as read at that moment. It cannot reverse. Ties go up, left, down, right. | Implement the look-ahead (a ghost keeps a `plan`). |
| 3 | Forced reversal | "Ghosts reverse when the mode flips" | Reversal is a signal. A ghost obeys it only once it enters its next tile. Reverses happen on chase to scatter, scatter to chase, and anything into frightened, never on frightened back. | Implement as a pending flag applied on the next step. |
| 4 | House release counters | Brief: Inky 30 and Clyde 60 on level 1, then "all at once from level 2" | Personal counters, one active at a time in the order Pinky, Inky, Clyde. Limits: level 1 = 0/30/60, **level 2 = 0/0/50**, level 3+ = 0/0/0. Idle timer: 4 s, **3 s from level 5**. After a lost life a global counter (Pinky 7, Inky 17, Clyde 32) replaces them. | Use the page's per-level limits and the 3 s idle timer. Keep the brief's simplification for lost lives (counters reset). This corrects an error in my brief. |
| 5 | Exit direction | Not in the brief | A ghost leaves the house going left, or right if a mode change happened while it was inside. | Implement (one flag). |
| 6 | Pac-Man speed | Constant per level | Pac-Man pauses 1 frame per dot (3 per energizer) and runs faster while ghosts are frightened (90/95/100%). | Not in the brief; leave out. It changes feel, so it is a candidate for slice 3 or later. |
| 7 | Frightened turn choice | Summary: "clockwise (up, left, down, right)" | The PRNG gives a first-choice direction. If blocked or a reverse, it tries the next one **clockwise** from it. The PRNG is reseeded with the same value on each new level and each lost life. The order "up, left, down, right" belongs only to chase tie-breaks. | Slice 3. |
| 8 | When frightened stops | Brief: 6 s, then 5/4/2 s in merged level groups, none from level 17 | Table A.1 (read at the start of slice 3) gives a **per-level** table that is not a smooth ramp. Seconds and flashes by level: 1: 6/5, 2: 5/5, 3: 4/5, 4: 3/5, 5: 2/5, 6: 5/5, 7: 2/5, 8: 2/5, 9: 1/3, 10: 5/5, 11: 2/5, 12: 1/3, 13: 1/3, 14: 3/5, 15: 1/3, 16: 1/3, 17: none, **18: 1/3**, 19 and up: none. Ghosts still reverse on an energizer when there is no blue time. | Slice 3 uses the page's table as data. This replaces the brief's merged rows, which the brief itself called my simplification. |
| 9 | Wave timer reset | Not in the brief | Resets when a life is lost and when a level is completed. Ghosts leave the house already in the first scatter. | Implement. |

## Confirmed as in the brief

Blinky targets Pac-Man's tile. Pinky targets 4 tiles ahead, and Inky doubles the vector from Blinky through the tile 2 ahead of Pac-Man. The page says the arcade has an upward-facing overflow bug in both (an extra left offset), which we do not copy. Clyde targets Pac-Man when 8 or more tiles away (straight-line distance) and his corner when nearer. Scatter targets are fixed tiles off the maze: Blinky top-right, Pinky top-left, Inky bottom-right, Clyde bottom-left. Eyes return to the tile above the left half of the door. Chain scores are 200, 400, 800, 1600. Speeds per level group match the brief's table.

## Still unread

Fruit and Cruise Elroy rows of Appendix A.1 (both cut from v1), the Appendix A.2 hard-difficulty table, and the later chapter on the split screen. None of them block the build. (Table A.1's frightened columns were read at the start of slice 3; see the last section.)

## Slice 3 additions (Table A.1 read)

- Frightened ghost speed is 50% on level 1, 55% on levels 2-4 and 60% from level 5, as in the brief. The page also speeds Pac-Man up while ghosts are frightened (90%, 95%, 100%). The brief left that out and v1 still does.
- Eaten-ghost eyes: the page gives their target (the tile above the left half of the door) and says they go in and are revived. It gives no speed for the eyes in the text I read. v1 runs them at full speed. That number is mine.
- Frightened flashing: the page gives a flash count per level, not a duration. v1 uses 0.25 s per flash. That number is mine.
- Cruise Elroy, fruit, the per-dot pause, and the level-256 split screen stay out of v1.
