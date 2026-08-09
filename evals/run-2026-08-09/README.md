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
count. The 22k perception saving is ~1% of a 3.2M billed total — while hybrid *carries* ~11k more
resident context across ~93 turns, which is ~1M billed tokens on its own. That is where the
saving goes.

Hybrid's context is the larger one despite the cheaper perception because the two arms buy
different kinds of token. Hybrid's spend is text that stays: 54.0k bytes/run of `exec` output
(the trees) vs bare's 32.7k, re-billed on every later turn. Bare's spend is images: 24.2
screenshots/run arriving through `read` (38.8k of its 47.5k tool tokens), against hybrid's 5.5.
Bare generates *more* total content (269.9k bytes of main-chain growth vs 209.1k) and still ends
with a smaller context, so a smaller share of what bare spends stays resident — consistent with
images not persisting the way text does, though this run doesn't isolate eviction directly. A
screenshot is expensive once; a tree is cheap and then charged forever.

Worth noting bare's *text* perception is the cheaper of the two (8.1k exec tokens/run vs hybrid's
13.5k): a grep over a dumped XML returns less than a rendered tree. Hybrid's perception advantage
is entirely that it does not need the screenshots.

So the lever on ACU is resident tokens per turn, not tokens per look. Defaulting a re-`see` to
the delta (this PR) is exactly that lever — it adds ~100 tokens to the context instead of
400-2,000, 59-66% less per re-observation on the bench. Turn count is the other half and the two
arms are identical there (93.3 vs 93.0, and the same batching density: 1.50 vs 1.48 UI actions
per exec that contains one), so a 30-task suite costs ~3 turns per task however you look at the
screen.

## Compose

Compose is the one stack where hybrid lost on perception (1.66x). It is one run: `seal|hybrid|1`
at 79.2k, of which 49.5k is images from 33 `hd shot` calls; the other three compose hybrid runs
average 14.9k against bare's 18.7k. The cause was a bug in `hd.py` — `render` only printed
`checked=` for nodes whose class was Switch/CheckBox/RadioButton/ToggleButton, but Compose emits
every switch as a bare `android.view.View` with `checkable="true" checked="true|false"`. Toggle
state was therefore invisible in the profile that also has no labels, and screenshots were the
only way left to read it. Fixed alongside this archive; `evals/test_toggle_state.py` regresses
it.
