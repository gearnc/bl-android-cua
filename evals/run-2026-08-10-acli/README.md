# Run, 2026-08-10 — 36 cells, three arms, plugin `main` @ 806d933

First A/B/**C**: the same 6 apps × 2 replicates as the earlier runs (markor/amaze Views,
seal/unitto Compose, joplin/lesspass RN, ~30 machine-verifiable tasks each, Normal capability,
fixed `adb` verification dump), but three arms —

| arm | prompt paragraph | what it had |
|---|---|---|
| `hybrid` | `ARM_HYBRID` | whatever tooling it has, i.e. the skill |
| `bare` | `ARM_BARE` | the skill denied, nothing offered instead |
| `acli` | `ARM_ACLI` | the skill denied, pointed at `accessibility-cli` |

Measured revisions, verified on a child VM before launch, not assumed:

* plugin `main` @ `806d933`, children's plugin cache byte-identical to it
  (`hd.py` and `SKILL.md` diffed against the checkout);
* `accessibility-cli` `0.1.0` @ `03cfeb3` (DioxusLabs/accessibility-cli), `cargo install`ed into
  the snapshot and on `PATH`;
* emulator Android 14 / API 34 at 720×1280, all six verification dumps `rc=0` and
  `test_acli.py` `problems=none` before any child was launched.

Ratios are against `bare`. Full writeup in [`report.md`](report.md).

> **The first collection of this run was censored and its numbers are withdrawn.** Event pages
> were paginated at `first=100`, which overflows the tool's output cap: each page was cut off
> mid-list but kept its "More results" cursor, so the walk continued and dropped the tail of
> every page. The event taken for each cell's *last* `context_growth_update` was therefore a
> mid-run one, at 24–100% of the cell's turns — `amaze|bare|1` was read at turn 69 of 243. It
> censored the slow-growing arm hardest, i.e. `bare`, the arm every ratio is against: perception
> read 0.95x hybrid/bare when it is 0.74x, and command capture read 74 of 234 exec calls on
> `amaze|hybrid|1`. Everything here is the complete re-collection; `gather.py` now raises on a
> truncated page and `README.md` documents the cross-check (last growth `iteration_count` vs.
> last `iteration_stats`).

## Headline

ACU **1.13x** hybrid / **1.30x** acli. Perception tokens **0.74x** / **1.06x**. Screenshots
**0.28x** / **1.15x**. Tasks done 27.6 / 28.2 / 28.2 of ~30 — reliability parity, no arm buying
its cost back in completions. Billed input (resident context integrated over turns) **1.28x** /
**1.31x** on the median run, which is the number that tracks ACU.

So the skill does what it claims per look — 469 perception tokens per observation against bare's
1,442, and a quarter of the screenshots — and still costs 13% more ACU.

## Why the cheaper arm is the one without the tool

ACU is inference: it tracks turns and the context each turn re-reads, not the price of a look.

| per run | hybrid | bare | acli |
|---|---:|---:|---:|
| commands before the first UI action | 7.3 | 9.9 | 22.9 |
| of those, writing its own tooling | 0.25 | 0.75 | 0.58 |
| looks per task | 4.14 | 2.68 | 3.38 |
| perception tokens per look | 469 | 1,442 | 689 |
| actions per look | 1.73 | 4.28 | 0.87 |
| commands firing ≥2 actions with no look | 11.6 | 21.5 | 7.3 |
| turns per task | 6.29 | 5.59 | 6.85 |
| ACU per turn | 0.0735 | 0.0719 | 0.0761 |

1. **Building the improvised tooling is free.** The bare agent writes its `uiautomator dump`
   wrapper in **0.75 commands** of a 157-turn run (one heredoc; `ui.sh`, `ui.py`, `t.sh`), inside
   the first two minutes, and it is ahead on commands-before-first-action anyway because the
   hybrid arm spends its own bootstrap locating `hd.py` and loading the skill. There is no setup
   tax to amortise, so nothing offsets the per-turn deficit.
2. **A cheap look gets spent on more looking.** Hybrid looks 4.14 times per task against bare's
   2.68 (+54%). Regressed across the 24 hybrid/bare cells, one extra look per task costs
   **0.053 ACU per task**, so the look-rate difference alone prices at **+2.15 ACU per run**
   against an observed gap of +1.85 — the whole deficit, with the token saving giving a little
   back. Looks-per-task is the strongest per-cell predictor of ACU after turn count itself.
3. **The bare agent acts blind twice as often.** 21.5 commands per run fire two or more actions
   with no observation attached, against hybrid's 11.6, and it gets 4.28 actions per look against
   1.73. It taps absolute coordinates it already knows (`input tap 640 1006`) and re-uses them
   later in the run; `hd tap N` indexes the *last* `see`, so any batch that crosses a screen has
   to go through `hd tap-xy` from notes (31 per run — used, but half as often as bare batches).
4. **More looks resident ⇒ a dearer turn.** Final context 121k hybrid vs 109k bare, and ACU per
   turn 0.0735 vs 0.0719. Decomposed: ACU 1.13x = turns 1.10x × ACU/turn 1.03x. Perception
   tokens, where hybrid wins 0.74x, are a fraction of a percent of what a run bills.

Where hybrid wins it is the same mechanism running the other way: on the RN apps the bare agent
could not grep its way through the tree and fell back to pixels (joplin bare: 40 and 72
screenshots, 101k perception tokens), and hybrid takes 0.93x/0.79x the ACU on joplin/lesspass.
The Compose and Views apps, where a `uiautomator dump` greps cleanly, are where it loses
(seal 1.48x, markor 1.23x, unitto 1.20x, amaze 1.14x).

**The tail is still worth reading.** Both tool-using arms have one app where they grind:

| cell | ACU | turns | exec calls | perception | screenshots | tasks |
|---|---:|---:|---:|---:|---:|---:|
| amaze\|bare\|1 | 19.1 | 243 | 233 | 38,495 | 3 | 28/30 |
| amaze\|hybrid\|1 | 21.2 | 242 | 234 | 43,961 | 3 | 28/30 |
| amaze\|acli\|1 | 26.5 | 308 | 244 | 105,687 | 58 | 28/30 |

**Bare-arm caveat.** On this run 1/12 bare runs improvised tree tooling (≤5 screenshots), 4/12
did real visual CUA (≥20), 7 in between; median 10 screenshots. So it is a mix leaning visual —
the *flattering* framing, unlike [`baseline-2026-08`](../baseline-2026-08/) and
[`run-2026-08-09`](../run-2026-08-09/), and closer to
[`run-2026-08-09-autodiff`](../run-2026-08-09-autodiff/). Perception ratios are not comparable
across runs whose bare arms did different things. **Do not compare the acli column against any
archived run** — no earlier run had this arm.

**acli adoption: 12/12** runs invoked the binary, so no cell is excluded from the ratio. 496 of
1,052 invocations went through a shell wrapper the agent defined (`source ~/ax.sh; A --llm-query`)
rather than the literal name — `make_report.py` counts those now; the literal-name regex alone
scored `amaze|acli|1` at 4 invocations when it made 42, which would have read as an abandoned
tool.

**Bypass counts** are balanced (6/12 hybrid, 7/12 bare, 6/12 acli touched device state directly),
so no app's ACU comparison is void on that ground.

## Mechanism the run paid for: `--find` silently killed the delta

`hd see --find` is the verb the hybrid arm types most (741 of 1,292 observation calls, 57%). It
renders the *full* tree — it must, so `hd tap` indexes stay valid — and stored its baseline
under `mode="find"`. The delta path required `prev["mode"] == mode`, so the next plain `hd see`
found no baseline of its own kind and printed the entire compact tree, with no "screen changed
too much" line to make that visible.

242 of the 495 plain `hd see` re-observations in this run (**49%**) directly followed a
`--find`/`--full`/`-q`. Measured on the emulator over the six matrix apps
(`evals/test_find_baseline.py`), that interleaving costs **47%** of the re-observation's
characters: 16 loops, 0/16 deltas and 35,253 chars on this revision against 11/16 deltas and
18,617 chars once baselines are keyed off the *rendering* instead of the verb.

That fix makes each look cheaper, which is necessary but not sufficient: this run says the
skill's remaining cost is the *rate* of looking, not the price of one.

## Caveats

* `billed_tokens` is the integral of resident context over turns from ~12 sampled
  `context_growth_update` events per cell plus the last one — a model of what ACU tracks, not a
  billing statement. It moves 1.28x where ACU moves 1.13x; trust ACU for cost, billed for
  mechanism.
* `exec_commands.json` is what the sessions API returned for `shell_process_started`. After the
  pagination fix it agrees with the growth aggregate's `exec` call count to within a few percent
  on most cells (hybrid 154 captured vs 160 counted), and is applied identically to every arm.

## Files

| file | contents |
|---|---|
| `runs.json` | cell -> child session id |
| `metrics.json` | ACU, turns, iterations, tool calls, screenshots, perception and billed tokens |
| `tasks.json` | `n_done` / `n_partial` / `n_failed` from each child's structured output |
| `bypass.json` | device writes, deep-link intents and disk reads per cell |
| `exec_commands.json` | every captured shell command, per cell (adoption sections read this) |
| `billed.json` | sampled-series shape behind `billed_tokens` |
| `report.md` | the generated writeup |
