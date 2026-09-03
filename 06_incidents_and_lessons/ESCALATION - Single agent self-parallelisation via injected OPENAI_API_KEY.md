# ESCALATION — A "single" agent can build its own swarm using the injected model key

> **Key clarification (to prevent misreading):** the credential in play is the **Fireworks API
> key** (`FIREWORKS_API_KEY`). The harness surfaces its value inside the container under the
> alias `OPENAI_API_KEY` only because Fireworks is OpenAI-API-compatible
> (`single_opencode.py:259-262`). No real OpenAI account/key is used anywhere — the task
> verifier, the run config, and every agent call all use Fireworks
> (`https://api.fireworks.ai/inference/v1`). Wherever this doc says `OPENAI_API_KEY`, read
> "the Fireworks key, aliased as `OPENAI_API_KEY`."

**Raised:** 2026-07-27 · **Updated:** 2026-07-28 (addendum 6b — structural root cause, measured)
**Severity:** Blocks any task whose multi-agent thesis rests on reading volume, corpus scale,
or context-window pressure — which is most Phase-2 `long_horizon` / `long_writing` tasks.
Addendum 6b generalises this: it blocks any task whose **deciding information fits in one
context**, regardless of how large the surrounding corpus is — and shows a task author cannot
fix that by choosing different checks, a deeper DAG, or a different output key.
**Status:** 3 designs killed at or after the design gate; the third is a complete, gate-passing
package retained as evidence. Total cloud runs spent proving it: 1 (plus 3 lost to a backend
sandbox flake, no agent execution).
**Evidence run:** `run_78db99ab49695894` (mode `single`, `kimi-k2p6`, daytona, 1h 58m 55s,
tokens in/out 1,863,793 / 86,077, cost $1.0652)
**Task:** `b1b701ceaf5447839847747a68f32b04-SWARMBENCH-SPECIALIST-PLANNING-OPERATIONS-RELEASE-CYCLE-TRIAGE-DOSSIER`
(700 real `microsoft/vscode` feature requests, ~431k input tokens, ~165k output tokens)

---

## 0. SCOPE CORRECTION 2026-07-29 — this is necessary but NOT sufficient. Read before acting.

Everything below is verified and stands. What was overstated is the *scope*: earlier revisions of
this document, and my own verbal framing, treated the injected key as **the** root cause of the
dead designs. Two later measurements show it is only one of two independent attack classes, and
scoping the key addresses only the first.

- **Key-dependent attack — fan out to inference APIs.** Needs the credential. This is what
  `run_78db99ab49695894` did (§2). Scoping the key kills it. Fully evidenced here.
- **Key-independent attack — deterministic scripting and retrieval, zero model calls.** Needs
  nothing at all, so no platform change touches it. Measured twice since:
  `_corpus_selection/extraction_control.py` — a ~100-line regex extractor answered **85.2%** of the
  appellate outcome judgment against a 33.3% chance floor. `_corpus_selection/constructed_control.py`
  — plain TF-IDF/BM25 answered the constructed comparison at **50.0% macro against an 11.1% chance
  floor**, and that judgment appears in NO source document, so nothing was extracted; the attack was
  nearest-neighbour retrieval plus reading off a formulaic disposition. Separately, the shard probe
  compressed the AD corpus **22x with every graded field intact**, again with no model.

**Consequence for the ask in §5:** the fix requested there is still worth making on its own merits —
an unscoped, unmetered production credential in an agent container is a real exposure regardless of
benchmark design. But do not expect the single-vs-multi gap to open once it lands. The appellate
designs died to the key-independent class, which the fix does not address.

**Frequency, measured 2026-07-29 with denominators.** A scan of all 13,222 execution-log files in the
workspace found `run_78db99ab49695894` to be the **only** instance of actual inference fan-out.
Denominators, so "n=1" can be read correctly:

| population | count | fan-out |
|---|---|---|
| single-agent run dirs with a substantive agent log | 132 | 1 |
| ...on the `single-opencode` runtime (the code path verified in §7) | 42 | 1 (**2.4%**) |
| ...distinct TASKS among those opencode runs | 28 | 1 (**3.6%**) |
| ...on the older `single-kimi` runtime (different code path, NOT verified) | 74 | 0 |

**Negative control that matters more than the rate.** `DELIVERY-WAVE-PLAN` was run single-agent 13
times on the same runtime with the same key available, including `_cloud_runs/single700` at 700 units
— comparable scale to b1b7. All show **zero** `chat.completions.create`, zero `pip install openai`,
zero `nohup`, zero `max_workers`. Scale alone does not trigger the behaviour.

The runner-up by raw match count, the harness example `7cac0ea2...COUNTY-SERVICE-DEPENDENCY-SWEEP`
single run, is a false positive: its `api.fireworks.ai` hits are the opencode config's own `baseURL`
and its `ThreadPool` mentions are reasoning text about parallelising GitHub scraping. The ~8-match
tier elsewhere is the same scaffolding baseline, present identically in single AND multi runs.

**How to state the ask, then.** The CAPABILITY is structural and always present (verified in code,
both arms, every opencode run). The BEHAVIOUR is rare and non-deterministic: 1 in 42. Do not claim
agents do this routinely — that is false and a reviewer will check. The correct argument is about
REPRODUCIBILITY, not frequency: **when the SA score depends on whether the agent happens to run
`env | grep -i key`, the arm is no longer a measurement.** A 2.4% branch that swings SA from ~0.30 to
0.88 (§3) makes the gap a coin flip, and re-running until SA scores low would be selecting the runs
where the agent failed to notice — which is not a capability finding.

**Also stated plainly: the counterfactual was never run.** No single-agent run was ever executed
with the key withheld. Every claim here about what the agent DID is measured from its trajectory;
any claim about what it WOULD have scored without the key is inference, not measurement. If a
measured number is needed to support the ask, re-run `b1b7` single with the credential withheld.

## 1. Summary

The single-agent arm did not solve the task as one agent. It discovered the Fireworks
credential that the harness injects into the container, installed the `openai` client, and
fanned the per-item work out across a thread pool and several models. It therefore behaved as
a multi-agent system while being scored as the single-agent baseline.

The consequence is not that this one task scored badly. It is that **"a single agent cannot
hold 431k tokens in a 262k context" is not a durable capability claim**, because a ~40-line
script makes the context window irrelevant. Any task whose gap comes from corpus size is
open to the same move.

## 2. What the agent did, in its own trajectory

Ordered evidence from
`execution_logs/single-opencode-agent/b1b701ceaf5447839847747a68f32b04__zuWSHsS/agent/opencode.txt`:

1. **Second bash command of the run** — it went looking for credentials before doing any work:
   `env | grep -i openai; env | grep -i api; env | grep -i key; ls /usr/local/bin/ | grep -i ollama`
2. `pip install openai -q`
3. Confirmed the key was live:
   `curl -s https://api.fireworks.ai/inference/v1/models -H "Authorization: Bearer $FIREWORKS_API_KEY"`
4. Tuned batch sizes (`test_batch_sizes.py`, `test_5.py`, `test_10.py`) for ~23 minutes.
5. At 33.7 min, launched **sharded background workers**:
   `nohup python3 /workspace/worker.py 0 88 > /workspace/stdout_0_88` (88-item shards).
6. At 113.5 min, `run_all_threads.py`.

Measured over the whole trajectory:

| observation | value |
|---|---|
| script sites calling `chat.completions.create` | 18 |
| worker pool width | `max_workers=5` |
| distinct models it called itself | 5 — `kimi-k2p6`, `deepseek-v3`, `llama-v3p1-70b-instruct`, `llama-v3p1-8b-instruct`, `qwen2p5-72b-instruct` |
| its own `read` tool calls | 3 |
| its own output tokens | 86,077, against a ~165,000-token deliverable |

The last two lines are the tell: it barely read the corpus itself, and roughly half the
delivered content was generated by delegated calls that never entered its context.

## 3. Why this defeated the task's design

The rubric was built to catch a serial agent degrading over a long backlog. It could not,
because each delegated shard ran in a fresh context:

| check | single-agent result |
|---|---|
| assessments delivered | 700 / 700 |
| schema-valid records | 700 / 700 |
| verbatim evidence quotes | 700 / 700 |
| routing (demand tier + owning area) | 700 / 700 |
| deferral identity (true top-25 excluded from the slate) | 25 / 25 |
| **full-output depth band, tail vs head degradation** | **0.00 — no degradation at all** |

Independent audit of the artifact (stricter than the verifier's own metrics) confirms the work
is genuinely good, not templated: 700/700 distinct sentence skeletons, zero near-duplicate
pairs at 0.30 4-gram Jaccard, 4,279 distinct content words, and only 1/700 rationales with
largely copied source vocabulary.

**Score:** the delivered run reported `0.0`, but only because of an unrelated packaging bug on
our side (a CRLF `tests/test.sh`, so the shebang resolved to `/bin/bash\r` and the verifier
never executed — fixed, with a static guard added). Re-grading the identical artifact offline
with the shipped verifier gives **0.5598 on the 14 deterministic checks with all 8 LLM judges
failing closed to 0.0**. Since the judges assess semantic quality of rationales that the audit
above shows to be sound, the true score is materially higher — our estimate is ~0.8. Against
any plausible multi-agent score this leaves a gap far below the 0.23 floor.

## 4. Why we cannot fix this inside a task

The obvious mitigation — air-gap the environment — is unavailable, for two independent reasons.

**The agent needs the key and the network to function at all.**
`harbor/src/harbor/agents/installed/swarmbench/single_opencode.py` (~line 259):

> `# Fireworks is openai-compatible; surfaced as OPENAI_API_KEY in the container`
> `env["OPENAI_API_KEY"] = fw_key`

The agent process runs inside the container and reaches its model over the same egress path it
used to fan out. `allow_internet = false` appends
`harbor/src/harbor/environments/docker/docker-compose-no-network.yaml`, which sets
`network_mode: none` on the **main** service — the agent's own service. So air-gapping does not
constrain the agent; it stops the trial from running.

**It would also silently destroy LLM-judge grading.** The verifier executes in that same
environment (`harbor/src/harbor/trial/trial.py`, `run()` → `_run_verification()` at ~line 991,
using `self._environment`), so with no network every judge fails closed to 0.0. We hit exactly
this: our first pass set `allow_internet = false` on integrity grounds and would have graded
both arms on the deterministic subset alone.

Note also that **no approved sample task sets `allow_internet` at all** — every one of the 17
we checked leaves it at its `true` default. The exposure is therefore systemic and pre-existing,
not something this task introduced. It only becomes decisive once a task is large enough that
writing the fan-out is worth the agent's while.

Task-level countermeasures we considered and rejected:

- *Forbid it in `instruction.md`.* Unenforceable, and this agent explicitly reasoned about the
  "no delegation" instruction before deciding a script was permissible.
- *Detect it in the verifier and zero the run.* A structural gate that zeroes a valid
  submission is forbidden by the scoring rules, and the verifier cannot see the agent's
  workspace or shell history in any case.

## 5. What we are asking for

Any one of these would restore the single-agent baseline:

1. **Withhold the model credential from the agent's shell environment.** Let the agent runtime
   hold it out of band (proxy, unix socket, or a wrapper the agent cannot read) so `env` does
   not surface a general-purpose inference key to arbitrary `bash`.
2. **Egress-allowlist to the harness's own model endpoint, per-identity.** If the agent can only
   reach the model through the harness's instrumented path, self-issued fan-out is visible and
   attributable — and its token use would land in the trial's accounting instead of being
   invisible, as the 86k-vs-165k discrepancy shows it currently is.
3. **Give the verifier a network path independent of `allow_internet`.** This is worth doing
   regardless: it decouples "should the agent browse" from "can the judge be reached", which are
   currently the same switch and pull in opposite directions.

Option 3 alone does not fix the exposure, but combined with 1 or 2 it lets a task be
genuinely air-gapped for the agent while still being LLM-judged.

### 5a. Concrete change, smallest viable version

Stated precisely so this can be actioned without re-deriving it. The single-agent injection is at
`harbor/src/harbor/agents/installed/swarmbench/single_opencode.py` (~line 259):

```python
# Fireworks is openai-compatible; surfaced as OPENAI_API_KEY in the container
env["OPENAI_API_KEY"] = fw_key
```

**Removing that alias alone fixes nothing, and this is the trap to avoid.** The run config passes the
key to the agent *and* the verifier as two separate flags — from
`_local_runs/single-opencode-agent/lock.json`:

```
"--ve", "FIREWORKS_API_KEY=${FIREWORKS_API_KEY}",   # verifier env
"--ae", "FIREWORKS_API_KEY=${FIREWORKS_API_KEY}",   # AGENT env
```

So `FIREWORKS_API_KEY` is in the agent's environment under its own name, independently of the
`OPENAI_API_KEY` alias — and the `b1b7` agent used exactly that name to confirm the key was live:
`curl -s https://api.fireworks.ai/inference/v1/models -H "Authorization: Bearer $FIREWORKS_API_KEY"`.
**Both the `--ae` passthrough and the alias must go.** The same alias exists in the multi arm at
`multi_opencode.py:307-310`, so any fix must be applied to both files or the arms become asymmetric.

Three further points matter for scoping the fix:

- **The verifier does not need the agent's copy.** It receives the key through `--ve` in a separate
  process at grading time, so dropping the agent-side `--ae` passthrough and the alias does not touch
  judge grading. These are independent paths that happen to carry the same secret today.
- **The agent runtime does need model access**, so the credential cannot simply be dropped — it has
  to move somewhere `bash` cannot read it. The minimal form is a local proxy: bind an
  OpenAI-compatible listener on loopback inside the container, point the agent runtime at it with no
  credential, and hold the real key in the proxy process. `env` then surfaces nothing usable, while
  the agent runtime works unchanged.
- **A proxy also fixes the accounting hole** noted in section 3: the `b1b7` run delivered a
  ~165k-token artifact while reporting 86,077 output tokens, because delegated generation never
  entered the trial's accounting. Requests through a proxy are attributable by construction.

If a proxy is too invasive for now, a **per-run key scoped to the model the agent is running as,
with a low concurrency cap**, would blunt the exploit without new infrastructure: fan-out across five
models becomes impossible and a five-wide worker pool becomes rate-limited rather than free. This is
strictly weaker than the proxy — it constrains the exploit's efficiency, not its availability — but
it is a config change rather than a code change.

**Verification that a fix worked**, reusable as a regression test: re-run the `b1b7` single arm and
assert all four of these, each greppable from the execution logs that already exist —

1. `env` inside the agent container surfaces no working inference credential under **any** name
   (check `FIREWORKS_API_KEY` and `OPENAI_API_KEY` explicitly; `b1b7`'s second bash command was
   `env | grep -i openai; env | grep -i api; env | grep -i key`).
2. A direct `curl` to `https://api.fireworks.ai/inference/v1/models` from the agent shell fails.
3. The trial's reported output tokens are within a plausible factor of the delivered artifact's size
   (`b1b7`: 86,077 reported against a ~165,000-token deliverable).
4. The trajectory contains no `chat.completions.create` call sites outside the harness path
   (`b1b7`: 18).

## 6. Reproduction

```
mascloud run <task folder> --mode single
mascloud download <run_id> <dest>
# then, in the downloaded run:
#   execution_logs/**/agent/opencode.txt   -> grep for chat.completions.create, max_workers
#   execution_logs/**/agent/assessments.json -> 700/700 complete
```

Trainer-side analysis scripts used for the numbers above (not shipped with the task):
`audit_sa_trajectory.py`, `audit_sa_artifact.py`, `coverage_sweep.py`, `check_correlation.py`.

## 6a. ADDENDUM 2026-07-27 — a second, independent, quantified data point

Since raising this we designed a replacement task on a deliberately fan-out-resistant axis and
killed it **at the design gate, before spending a cloud run**. The measurement is the reason we
now believe this is a platform-level blocker rather than a run of unlucky task designs.

**What was tested.** A Falcon fleet airworthiness-directive status review: 156 real Dassault ADs
pulled from govinfo.gov (2,918,373 characters, ~730k tokens, ~2.8x a 262k context window), 74
supersession edges recomputed from the frozen text, 20 real N-registered Falcons with real serial
numbers, 418 required determinations. Thirty-one ADs carry applicability conditions an operator's
records genuinely cannot answer, e.g. verbatim: *"all serial numbers except those on which
Dassault Aviation Modification M724 is embodied."* The design deliberately avoided everything
`b1b7` was faulted for: the discriminating layer was cross-item coherence (a shared interpretation
policy binding 129 determinations), not per-item assessment or reading volume.

**Result — 14 deterministic checks, one point each:**

| profile | what it models | score |
|---|---|---|
| cheapest one-shot fan-out | exactly what `b1b7`'s agent ran (`worker.py` + ThreadPool) | 10/14 = **0.71** |
| scripted fan-out | 162 independent extraction calls, then determinations, policy and the entire coherence layer computed deterministically in Python | 13/14 = **0.93** |
| honest serial single agent | truncates at 35% coverage | 4/14 = **0.29** |
| ideal swarm | complete and correct | 13/14 = **0.93** |

**The scripted fan-out ties the ideal swarm exactly. Gap 0.00.** The gate ceiling was 0.40.

**Why this matters more than one dead design.** Every check we could write fell into one of two
classes, and the single agent wins both:

1. **Per-item** checks are the shape `b1b7` already proved fan-out eats.
2. **Cross-item coherence** checks — consistency within a condition class, precedent-citation
   validity, rollup reconciliation, "no superseded directive marked applicable" — *look* like
   coordination measurements but are satisfied **by construction** by a script. It computes the
   classes and assigns the identifiers, so it is perfectly self-consistent, and more reliably so
   than a real agent is.

The generalisable form: **a cross-item obligation only resists fan-out if the state it carries
cannot be reconstructed by a script.** Compact structured state — id sets, resolved graphs, class
indexes, running budgets — is threadable through independent prompts and therefore scriptable.
Staged or "round-based" designs do not help: a script wraps its worker pool in a loop over rounds.

The only profile that scored low was the honest serial agent, and it scored low purely on
**coverage** — which is precisely what a ~$1 fan-out buys.

**Hardenings we considered and rejected on integrity grounds**, rather than shipping them:

- Requiring retroactive revision when a later directive supersedes an earlier one. A script
  computes supersession up front and never makes the superseded determination at all. Penalising
  that penalises the better method, and a revision obligation with no required population is
  vacuously satisfiable.
- Requiring an inductively-amended policy. An agent that reads all instances before writing the
  rule legitimately needs no amendment; mandating one grades the *order of work* rather than the
  outcome, which is a manufactured gap.

**Corroboration across the whole workspace.** No task we have run has reached the 0.23 gap floor:
`be59` peaked at MA 0.787 / SA 0.66, `a947` at MA 0.784 / SA 0.723, `b1b7` at SA ~0.85. The single
historical 0.30 gap came from a stacked depth band with graduated cutoffs and was rejected by the
client as post-hoc calibration.

**A second shape was tested and failed identically.** "Shared mutable state under contention" —
20 airframes competing for 40 maintenance-line slots, demand exactly saturating supply — was the
one shape we believed a fan-out would actively damage rather than merely match. A ~30-line
deadline-sorted greedy allocator scored **7/7 = 1.00**, tying the ideal swarm again (gap 0.00).
It also surfaced a second-order problem: contention checks are coverage-blind by construction
("no double booking" is easiest to satisfy by booking nothing), so a truncated serial agent scored
the same 0.71 as the cheap fan-out.

**The result stated formally.** Both arms are programs with LLM-oracle access, in the same
container, with the same credential, shell and tools. Their computational capability is therefore
identical — any function the swarm computes, a script in the single-agent container can compute.
What differs is only (i) whether the agent in fact organises the work well, and (ii) wall-clock,
which is uncapped for both on long-horizon tasks. **Under the current configuration the benchmark
cannot measure a capability gap; it can only measure a behavioural one.** The two premise tests
bracket that behavioural gap at **0.00 against a competent scripted attacker and +0.29 against a
naive one** — and which one a live run reports is decided by whether that particular agent chose
to write ~40 lines of Python.

**What this adds to the ask in section 5.** Section 5's options were framed as restoring one
task's baseline. On this evidence they are prerequisites for the benchmark measuring coordination
at all: while an arbitrary `bash` can read a general-purpose inference key, the single-agent arm
is not a single agent, and any gap a task reports is a measure of whether that particular agent
happened to write the script — not of coordination capability. Option 1 (withhold the credential
from the agent shell) or Option 2 (per-identity egress allowlist to the harness's instrumented
endpoint) remain the asks; Option 3 (an independent network path for the verifier) is what makes
either of them compatible with LLM-judged grading.

Full analysis: `PREMISE_TEST_FINDING_falcon_ad_review.md`. Reproducible harness:
`phase_2_tasks/phase_2_1_tasks/task2/_trainer_artefacts/premise_test.py` — it recomputes every
expectation from the frozen input (no oracle), expresses the rubric as executable boolean checks,
synthesises the four profiles above and prints the per-check matrix. Cost to reach this verdict:
**zero cloud runs.**

## 6b. ADDENDUM 2026-07-28 — the structural reason, measured: size the DECIDING SLICE, not the corpus

The two premise tests in 6a were empirical ("we tried, the script tied us"). This addendum gives the
**structural** reason, from a third design carried all the way to a complete, gate-passing package
before being measured honestly. It is the sharpest form of the argument and it generalises beyond
these three tasks.

**The design.** `dcdb45b6…-FLEET-AIRWORTHINESS-POSITION-PAPER`: the AD compliance position a Part 135
operator files before its Principal Maintenance Inspector issues operations specifications. 156 real
FAA directives verbatim from govinfo.gov (2,918,373 characters, ~730k tokens, ~2.8x a 262k context),
24 real Falcon airframes verified row-by-row against the OpenSky registry, 95 in-force directives,
503 determinations, 92 unresolvable pairs. 21 checks, one point each; 15 deterministic and recomputed
from the directives' own paragraphs, 6 different-family judges failing closed. It passes corpus
integrity, fleet integrity, static checks S-01..S-07, an empty-submission floor of exactly 0.000, and
a correlation test at 4/15 clustered.

**The measurement that killed it.** The gap thesis rested on a cross-corpus reconciliation: no
directive announces its own retirement, so the in-force set exists only after paragraph (b) of all
156 documents has been read and merged. True — and nearly free:

| slice | chars | ~tokens | share of one 262k context |
|---|---|---|---|
| paragraph (b), whole corpus — **decides the in-force set** | 14,285 | 3,571 | **1.4%** |
| paragraph (c), whole corpus — decides applicability | 52,527 | 13,131 | 5.0% |
| (b) + (c) together | 66,812 | 16,703 | **6.4%** |
| full corpus | 2,918,373 | 729,593 | 278% |

**The entire "merge that cannot fit in one slice" fits ~73 times over.** The 2.9M characters are
real, but they are overwhelmingly paragraphs (d) onward — unsafe-condition discussion and required
actions — which is *per-directive input to per-directive writing*. Corpus size was never the barrier;
we were measuring the wrong quantity. (The false claim has been corrected in place in that task's
`why_multi_agent`, with these numbers.)

**Information-locality census of the rubric.** Classifying all 21 checks by where the deciding
information lives:

| locality | checks | consequence |
|---|---|---|
| answerable from **one directive** + the fleet list | 15 | a per-directive shard gets these |
| cross-corpus but a cheap second pass solves it | 2 | 3.5k tokens; no barrier |
| genuinely **airframe-keyed or aggregate** | 4 | the only fan-out-resistant surface |

So the **maximum fan-out resistance this rubric can express is 4 points of 21 ≈ 0.19**. A fan-out
that reads every directive well and fails all four still scores ~0.81. No swarm beats that durably.

**Two candidate hardenings tested against the real corpus and abandoned — with numbers, before
designing on them:**

1. **Termination credit** (a tail's status for AD-A depending on AD-B's *resolved outcome for that
   same tail*) would be genuine dependency on resolved answers, which is the property section 6a
   identified as necessary. The corpus contains **4 `terminates` edges, 1 with its victim in the
   corpus, 0 behind a configuration condition**, against 69 `supersedes` and 59 `affects`. No spine
   exists to build on.
2. **Re-keying the deliverable** so its unit cross-cuts the corpus unit (per-airframe output over a
   per-directive corpus) is defeated by a two-stage fan-out: shard per directive to build a compact
   index (tails reached, requirement, quote — well under 1k chars each), then shard per airframe over
   the ~95k-char index. **Per-tail status is a relational join over per-directive facts, and joins
   parallelise.**

**The generalisable rule we now apply at Gate 1.** Extract *only* the fields or paragraphs that
determine each graded answer and measure **that** in tokens. If the deciding slice fits in one
context, the task has a correctness trap that punishes carelessness but **no capacity barrier**, and
no amount of total-corpus scale changes it. Bulk that is per-unit input to per-unit writing is
parallel work, not coordination work. Two further non-defences, both previously believed to help:
**dependency depth creates ordering, not a parallelism requirement** (one agent walks a 9-level DAG
sequentially), and **volume alone is parallel by construction**.

**What this adds to the ask.** Sections 5 and 6a asked for the credential to be withheld or egress to
be allowlisted. This addendum explains why no task-side redesign substitutes for that: the fan-out
wins because the deciding information is *small and available at shard time*, and a task author
cannot make a real corpus's deciding information large by choosing different checks or a different
output key. Only the platform can make it unavailable at shard time. Until then the honest ceiling on
what any of these tasks measures is **designed coordination versus improvised coordination** — a real
axis, but not the capability gap the benchmark is specified to measure, and one where the improvised
arm currently scores *higher* (0.649 vs 0.544 on this task's deterministic floors).

Reproducible, zero cloud runs: `phase_2_tasks/phase_2_1_tasks/task2/_trainer_artefacts/` —
`fanout_delta.py` (per-check swarm-vs-fan-out matrix), `fixtures.py` (26 profiles, per-axis error
dials, coverage sweep, correlation test), `verify_fleet.py` and `verify_sources.py` (integrity), and
`NOTES.md` for the full decision log.

## 7. Secondary finding (ours to fix, recorded for completeness)

The rubric was less discriminative than its 22-check count suggests. Across 11 graded fixture
profiles, 10 of the 14 deterministic checks fall into clusters correlating at r ≥ 0.95
(`completeness_validity` ↔ `grounding_integrity` ↔ `routing_and_rollup` at r ≈ 1.000;
`funding_argument_quality` ↔ `deferral_reason_quality` at 0.999), and 8 of 22 points are
reachable by "emit every record, well-formed, with varied prose". Future rubrics should be
correlation-tested against fixture profiles before a live run, not just count-checked.
