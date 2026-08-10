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

## Headline

ACU **1.13x** hybrid / **1.30x** acli. Perception tokens **0.95x** / **1.45x**. Tasks done
27.6 / 28.2 / 28.2 of ~30 — reliability parity, no arm buying its cost back in completions.
Billed input on the median run is at parity (3.19 / 3.09 / 3.09 Mtok); the means diverge
(6.52 / 3.17 / 8.06 Mtok) entirely because of the tail.

**The tail is the whole story.** Both tool-using arms have one app where they grind:

| cell | ACU | turns | exec calls | perception | tasks |
|---|---:|---:|---:|---:|---:|
| amaze\|bare\|1 | 19.1 | 69 | 64 | 11,168 | 28/30 |
| amaze\|hybrid\|1 | 21.2 | 242 | 234 | 43,961 | 28/30 |
| amaze\|acli\|1 | 26.5 | 308 | 244 | 105,687 | 28/30 |

Same app, same tasks, same score, 3.5× the turns. Per *look* the tool arms are not expensive —
188 perception tokens per exec call for hybrid against bare's 175 — they simply look far more
often, one verb at a time, where the bare agent's improvised `act.py` chains
`tap … text … sleep … show` into a single call and re-observes once. Cheap looks are not a cheap
run; that is the same lesson `--llm` teaches in the acli arm.

**Bare-arm caveat.** 7/12 bare runs improvised tree tooling (≤5 screenshots), 1/12 did real
visual CUA (≥20), 4 in between; median 4 screenshots. So this run measures *skill vs.
agent-improvised tree tooling* — the harsher framing, and the same one as
[`baseline-2026-08`](../baseline-2026-08/) and [`run-2026-08-09`](../run-2026-08-09/), but the
opposite of [`run-2026-08-09-autodiff`](../run-2026-08-09-autodiff/), whose bare arm was mostly
visual. That is why hybrid's perception ratio moved from 0.51x to 0.95x: different bare arm, not
a regressed skill. **Do not compare the acli column against any archived run** — no earlier run
had this arm.

**acli adoption: 12/12** runs invoked the binary, so no cell is excluded from the ratio. 117 of
340 invocations went through a shell wrapper the agent defined (`source ~/ax.sh; A --llm-query`)
rather than the literal name — `make_report.py` counts those now; the literal-name regex alone
scored `amaze|acli|1` at 4 invocations when it made 42, which would have read as an abandoned
tool.

**Bypass counts** are balanced (3/12 hybrid, 1/12 bare, 2/12 acli touched device state directly),
so no app's ACU comparison is void on that ground.

## Mechanism the run paid for: `--find` silently killed the delta

`hd see --find` is the verb the hybrid arm types most (214 of 416 observation calls, 51%). It
renders the *full* tree — it must, so `hd tap` indexes stay valid — and stored its baseline
under `mode="find"`. The delta path required `prev["mode"] == mode`, so the next plain `hd see`
found no baseline of its own kind and printed the entire compact tree, with no "screen changed
too much" line to make that visible.

73 of the 185 plain `hd see` re-observations in this run (**39%**) directly followed a
`--find`/`--full`/`-q`. Measured on the emulator over the six matrix apps
(`evals/test_find_baseline.py`), that interleaving costs **47%** of the re-observation's
characters: 16 loops, 0/16 deltas and 35,253 chars on this revision against 11/16 deltas and
18,617 chars once baselines are keyed off the *rendering* instead of the verb.

## Caveats

* `billed_tokens` is the integral of resident context over turns from 8 sampled
  `context_growth_update` events per cell — a model of what ACU tracks, not a billing statement.
  The amaze cells show it diverging from ACU by ~6x where ACU moved 1.14x; trust ACU.
* `exec_commands.json` is what the sessions API returned for `shell_process_started`, and on the
  busiest cells that is fewer events than the growth aggregate's `exec` call count
  (amaze|hybrid|1: 74 captured against 234 counted). Command-derived counts here are lower
  bounds, applied identically to every arm.

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
