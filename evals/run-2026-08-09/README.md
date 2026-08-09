# Run, 2026-08-09 — 24 cells, plugin `main` @ 367fe0a

6 apps (2 per toolkit: markor/amaze Views, seal/unitto Compose, joplin/lesspass RN) × hybrid/bare
× 2 replicates, Normal capability, ~30 machine-verifiable tasks each. Measured the plugin as of
`367fe0a` — i.e. **with** `hd see --diff` (PR #2) and the eval harness (PR #3), and before the
auto-diff change this run motivated.

Headline vs. the [August baseline](../baseline-2026-08/) (126 runs, pre-`--diff`): reliability is
still at parity (28.2/30 hybrid vs 28.4/30 bare), ACU is still at parity (1.02x, was 1.07x;
permutation p=0.86 on 12 v 12, i.e. no detectable difference either way), and
perception tokens moved from 0.94x to **0.50x** hybrid/bare. The tail is where the arms separate:
worst hybrid run 79k perception tokens vs 186k bare; bare p90 32.6k vs hybrid 20.6k.

**Bare-arm caveat.** 5/12 bare runs improvised tree tooling (<=5 screenshots), 2/12 did real
visual CUA (94 and 121 screenshots), 5 sat in between. The bare arm's perception mean is
dominated by those two runs, so the headline ratio is "skill vs. a mix of improvised tree
tooling and pixels", not "skill vs. screenshots". `report.md` states this per run.

**Read the ACU section before quoting the perception ratio.** 0.50x perception is not 0.50x cost:
billed tokens are at parity (median 3.17 vs 3.08 Mtok excluding four tail runs), and the skill's
measured value in this run is reliability parity at cost parity, not a cost win.

**Mechanism found.** `hd see --diff` was effectively unadopted: 8 invocations across all 12
hybrid runs, zero in 8 of them, against 217 plain/`--full` re-reads. The two most expensive
hybrid runs are both re-read loops — `amaze|hybrid|1` paged the full tree with
`hd see --full | head -40` / `sed -n '55,100p'` 14 times (246 iterations, 49.3k tokens), and
`seal|hybrid|1` fell back to 33 screenshots to read Compose toggle state (79.2k tokens). The
saving existed but was behind a flag nobody typed, which is why the fix makes the diff the
default for a re-`see`.

- `runs.json` — cell → session id (the sessions themselves are the ultimate audit trail)
- `metrics.json` — ACU, perception tokens, screenshots, iterations, exec calls per cell
- `tasks.json` — n_done / n_partial / n_failed per cell
- `bypass.json` — UI-bypassing shortcut commands per cell
- `billed.json` — turns, peak context and billed input tokens per cell (see below)
- `report.md` — the full writeup

## What bounds ACU — why 0.50x perception is 1.02x ACU

ACU is mostly inference, so it tracks *billed* tokens, and billed input is not what a look costs
once — it is the integral of the resident context over turns, because every token added at turn
i is re-read at every turn after i. Integrating each run's `current_context_tokens` series
against `iteration_count` gives billed input directly:

| | hybrid | bare |
|---|---:|---:|
| billed input, median | 3.23 Mtok | 3.18 Mtok |
| billed input, mean | 6.21 Mtok | 4.64 Mtok |
| peak resident context | 80,288 | 69,278 |
| turns | 93.3 | 93.0 |
| perception tokens | 22,305 | 44,624 |

Billed tokens are at parity at the median (the means are skewed by the four >190-iteration runs),
which is exactly what ACU reports; `acu` correlates 0.72 with billed input and 0.77 with turn
count. The scale is the first thing to notice: a whole run's perception spend, 22k tokens, is
~1% of a 3.2M billed total, because what dominates is re-reading the resident context ~93 times.
Halving perception moves ~0.3% of the bill. Any claim that a perception change moves cost has to
be argued in resident tokens per turn, and even there the effect is second-order next to turns.

### The arm means are tails; the medians are the same run

Four runs exceed 150 turns and they set every mean in this dataset:

| run | turns | exec tokens | screenshots | billed | what happened |
|---|---:|---:|---:|---:|---|
| `amaze\|hybrid\|1` | 246 | 37,421 | 7 | 22.1 Mtok | paged the full tree with `--full \| head`/`sed` |
| `seal\|hybrid\|1` | 248 | 28,621 | 33 | 20.7 Mtok | screenshotted Compose toggles (the `checked=` bug) |
| `amaze\|bare\|2` | 268 | 4,118 | 121 | 12.9 Mtok | visual CUA |
| `joplin\|bare\|1` | 217 | 5,961 | 94 | 12.2 Mtok | visual CUA |

Both arms blew up 2/12 times, and **hybrid's blowups are the more expensive**: 22.1 and 20.7 Mtok
against bare's 12.9 and 12.2, because a text loop inflates turns as well as tokens. The reported
0.50x perception ratio is largely an artifact of which *kind* of token each arm's tail spends —
bare's tails buy images (expensive per look), hybrid's buy trees (cheap per look, many more
looks) — and it inverts once you bill by context.

Drop those four and the two arms are the same run:

| median, 10 runs/arm | hybrid | bare |
|---|---:|---:|
| billed input | 3.17 Mtok | 3.08 Mtok |
| turns | 64 | 62 |
| exec calls | 53 | 50 |
| exec tokens | 9,714 | 7,840 |
| peak context | 68,831 | 65,374 |
| screenshots | 2 | 7 |
| ACU | 12.5 | 11.4 |

So the honest reading is not "the skill is cheaper" and not "residency eats the saving". It is
that in the normal case the skill is a wash (+3% billed tokens, within noise), it buys that wash
by trading 5 screenshots for ~1.9k more text tokens, and everything else in this dataset is tail
behaviour.

### Where the residual text gap comes from

Bare, having to build its own tooling, consistently builds one thing the skill does not do:
**it separates capture from retrieval**. It dumps the tree to a file (10.2 raw dumps per run,
which cost nothing in context because nothing is printed) and then greps it (6.0 filtered reads),
so only the matching lines are ever billed. `hd see` fuses the two: every observation renders a
tree into the transcript. Per run, hybrid issues 14.0 `--find`, 10.9 whole-tree `see`, 1.5
`--full` and 0.7 `--diff` — i.e. ~27 observations against bare's ~17, and 12.4 of them print
everything on the screen when the agent wanted one node.

That, not residency, is the mechanism behind hybrid's extra ~1.9k text tokens per run, and it is
also why the skill can lose: its cheapest verb is a whole tree, while the improvised tool's
cheapest verb is a grep. Defaulting a re-`see` to the delta (this PR) closes most of it — a
re-observation of a screen already seen adds ~100 tokens instead of 400-2,000, 59-66% less on the
bench — and it targets exactly the `amaze|hybrid|1` failure mode.

Turn count is the other half of billing, and there the arms are identical (93.3 vs 93.0 overall,
64 vs 62 excluding blowups, at the same batching density of 1.50 vs 1.48 UI actions per exec that
contains one): a 30-task suite costs ~3 turns per task however you look at the screen.

## Compose

Compose is the one stack where hybrid lost on perception (1.66x). It is one run: `seal|hybrid|1`
at 79.2k, of which 49.5k is images from 33 `hd shot` calls; the other three compose hybrid runs
average 14.9k against bare's 18.7k. The cause was a bug in `hd.py` — `render` only printed
`checked=` for nodes whose class was Switch/CheckBox/RadioButton/ToggleButton, but Compose emits
every switch as a bare `android.view.View` with `checkable="true" checked="true|false"`. Toggle
state was therefore invisible in the profile that also has no labels, and screenshots were the
only way left to read it. Fixed alongside this archive; `evals/test_toggle_state.py` regresses
it.
