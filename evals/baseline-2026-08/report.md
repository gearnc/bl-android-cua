# android-hybrid-navigation vs. unguided agent — 126-run blinded eval

**Matrix.** 21 apps x 2 arms x 3 replicates = 126 child sessions, Normal capability, 30 verifiable
tasks per app, one app per session. Every run booted the same emulator snapshot (Android 14, API 34,
720x1280 @320dpi, 35 F-Droid APKs preinstalled) and ended with a fixed `adb` state dump, so grading
is not self-report. Arms were blind: hybrid sessions got no instruction beyond "use whatever tooling
you have"; bare sessions were forbidden from reading or invoking the skill.

The plugin under test is post-PR #1 (Compose misdetection, off-screen swipes, unquoted `hd type`,
and the `hd` launcher all fixed) — measured on a snapshot rebuilt to pick up the merge.

## The caveat that reframes everything

**The bare arm is not screenshot-driven CUA.** Denied the skill, agents reinvented it: within the
first minute a typical bare session writes a `uiautomator dump` wrapper (`ui.sh`, `t.sh`, `ui.py`)
and greps it — `./ui.sh | grep -E 'firstline|fullpath'`. Median bare run: 2 screenshots across
~30 tasks. So this measures **the skill vs. agent-improvised tree tooling**, not the skill vs.
looking at the screen. It is the harsher question, and the honest label for these numbers.

I also checked the opposite failure — an arm completing tasks by writing device state instead of
driving the UI (`adb shell mkdir` for "create a folder"). It is rare and balanced: runs touching
device state directly, 6/63 hybrid vs 9/63 bare.

## Headline

| metric | arm | mean | median | cv | p90 | max |
|---|---|---|---|---|---|---|
| acu | hybrid | 12 | 12 | 0.40 | 18 | 28 |
| acu | bare | 12 | 11 | 0.29 | 16 | 19 |
| perception_tokens | hybrid | 18,090 | 13,765 | 0.73 | 47,798 | 59,544 |
| perception_tokens | bare | 19,213 | 14,860 | 1.19 | 21,660 | 186,113 |
| screenshots | hybrid | 3 | 1 | 1.56 | 6 | 23 |
| screenshots | bare | 6 | 2 | 2.54 | 8 | 112 |
| n_done | hybrid | 28 | 29 | 0.05 | 30 | 30 |
| n_done | bare | 28 | 28 | 0.05 | 30 | 30 |

At equal reliability (~28/30 tasks either way), **the skill is currently at parity on cost, not
ahead**: ACU 1.07x, perception tokens 0.94x. The README's ~30% token saving does not reproduce
against an agent that builds its own tree tooling.

What does reproduce is the **tail**. Bare's worst run burned 186k perception tokens and 112
screenshots (material_files); hybrid's worst was 59.5k. When an unguided agent's improvised tooling
fails it falls back to screenshot-thrashing, and the skill's floor holds. Hybrid uses half the
screenshots overall (mean 3 vs 6).

Against that, hybrid's own p90 is worse (47.8k vs 21.7k) — the skill has a fat upper-middle,
which is the finding PR #2 acts on.

## Where the skill loses: the observe-act-observe loop

Hybrid spends **+35% iterations and +37% exec calls** for the same work. Cost per observation is
the same in both arms (~190 vs ~200 tokens per exec call) — hybrid simply makes more of them, and
re-reads whole trees when it does: `seal|hybrid|3` spent 23 of its 37 `hd see` calls on unfiltered
dumps. Compose is worst (+23% tokens, +45% iterations), which is exactly where SKILL.md names the
full tree as the default primitive.


### ACU by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      10   0.50           10   0.31    1.00
rn                           11   0.39           10   0.39    1.01
views                        14   0.29           13   0.22    1.12
ALL                          12   0.40           12   0.29    1.07

### Perception tokens by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                   20555   0.75        16772   0.57    1.23
rn                        13460   0.14        17955   0.36    0.75
views                     17507   0.75        21543   1.49    0.81
ALL                       18090   0.73        19213   1.19    0.94

### Iterations by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      84   0.70           58   0.10    1.45
rn                           67   0.10           62   0.08    1.08
views                        90   0.81           66   0.54    1.36
ALL                          85   0.73           63   0.40    1.35

### Tasks done (of 30) by stack
stack               hybrid mean     cv    bare mean     cv   ratio
compose                      28   0.06           28   0.05    1.00
rn                           28   0.03           29   0.03    0.96
views                        29   0.04           29   0.04    1.00
ALL                          28   0.05           28   0.05    0.99

### ACU by app
app                 hybrid mean     cv    bare mean     cv   ratio
aegis                        16   0.33           12   0.12    1.28
amaze                        23   0.20           15   0.21    1.52
ankidroid                    11   0.11           13   0.21    0.87
antennapod                   10   0.07            9   0.04    1.16
blacksquircle                14   0.19           14   0.28    1.04
breezy_weather                3   1.09           10   0.08    0.31
feeder                       10   0.11            9   0.10    1.08
fossify_contacts             13   0.07           12   0.12    1.04
fossify_gallery              12   0.10           12   0.10    0.94
fossify_notes                15   0.05           11   0.05    1.36
jerboa                        5   0.21            5   0.04    1.17
joplin                       11   0.13           10   0.20    1.03
lesspass                      6   0.39            6   0.38    0.98
markor                       14   0.12           13   0.13    1.10
material_files               12   0.08           12   0.15    1.02
notesnook                    15   0.05           15   0.05    1.01
read_you                     12   0.10           11   0.10    1.13
seal                         17   0.07           12   0.26    1.48
tasks_org                    11   0.74           12   0.20    0.85
unitto                       10   0.24           10   0.21    0.96
wikipedia                    17   0.05           18   0.08    0.97
ALL                          12   0.40           12   0.29    1.07

### Perception tokens by app
app                 hybrid mean     cv    bare mean     cv   ratio
aegis                     26167   0.80        18661   0.19    1.40
amaze                     40177   0.60        25587   0.84    1.57
ankidroid                 11619   0.07        15750   0.22    0.74
antennapod                14105   0.17        15118   0.17    0.93
blacksquircle             29356   0.89        15256   0.17    1.92
breezy_weather            14416   0.05        22793   0.82    0.63
feeder                    10870   0.12        12804   0.21    0.85
fossify_contacts          11856   0.12        11686   0.18    1.01
fossify_gallery           12720   0.18        15734   0.22    0.81
fossify_notes             20901   0.77        11371   0.42    1.84
jerboa                    12314   0.20        12008   0.35    1.03
joplin                    15021   0.13        17227   0.19    0.87
lesspass                  11697   0.09        19906   0.56    0.59
markor                     9116   0.11        12520   0.29    0.73
material_files            13302   0.06        68889   1.47    0.19
notesnook                 13663   0.06        16732   0.27    0.82
read_you                  14640   0.14        11985   0.32    1.22
seal                      42203   0.50        14244   0.32    2.96
tasks_org                 25506   0.76        16528   0.13    1.54
unitto                    15133   0.04        28559   0.57    0.53
wikipedia                 15105   0.09        20116   0.10    0.75
ALL                       18090   0.73        19213   1.19    0.94

## Method notes

- Perception tokens are read off each session's final `context_growth_update` event:
  `approx_ant_tokens` for shell/tool output plus image tokens for screenshots, not estimated from
  transcripts.
- Variance is reported as coefficient of variation; the arms differ in scale, so an absolute SD
  would flatter whichever arm is cheaper.
- Jerboa caps at 25/30 in both arms — its remaining tasks need a logged-in Lemmy account, so both
  arms correctly report them impossible. Not a failure of either approach.
- Raw data: `runs.json` (cell -> session), `metrics.json`, `tasks.json`, `bypass.json`.

