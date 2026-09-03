# Premise-test finding: the Falcon AD-status-review design is dead, and the reason generalises

**Date:** 2026-07-27
**Design tested:** Falcon fleet airworthiness-directive status review with an evolving
applicability-interpretation policy (planning-operations, specialist-routing).
**Gate:** `NEXT_TASK_KICKSTART_fanout_resistant.md` section 3 — score the adversarial fan-out
against a draft rubric BEFORE building. Ceiling is ~0.40.
**Verdict:** the scripted fan-out scores **0.93** and is **indistinguishable from the ideal
swarm**. Design killed at the gate. No live run was spent.
**Artefacts:** `phase_2_1_tasks/task2/_trainer_artefacts/{premise_test.py,
premise_test_result.txt, freeze_corpus.py, structure_report.json}`

---

## 1. The corpus is real and was a good substrate

Everything below is real, public and frozen from key-free endpoints. The design did not die of
weak data.

| property | value |
|---|---|
| Dassault Aviation ADs (Federal Register RULE, 2010+) | 156 unique, text from govinfo.gov |
| total AD text | 2,918,373 chars (~730k tokens, ~2.8x a 262k context window) |
| ADs with a parsed `(c) Applicability` paragraph | 144 name a model |
| supersession edges recomputed from the frozen text | 74 |
| ADs whose applicability turns on a condition the operator's records CANNOT answer | 31 (23 modification-embodied, 8 service-bulletin-incorporated, 6 part-number-installed) |
| fleet | 20 real N-registered Falcons, real serial numbers (OpenSky registry aggregation) |
| required determinations (aircraft x in-force AD naming its model) | 418, of which 129 rest on an unresolvable condition |

A real applicability paragraph, verbatim, showing the genuine ambiguity the design was built on:

> "This AD applies to Dassault Aviation Model FALCON 7X airplanes, certificated in any category,
> all serial numbers except those on which Dassault Aviation Modification M724 is embodied."

## 2. The measured result

14 deterministic checks, one point each, graded on the deterministic subset only — the same way
`b1b7` was measured (SA scored 12.31/14 = 0.88 there with all judges off). LLM judges were
excluded because they historically lift BOTH arms and cannot rescue a design whose deterministic
layer a script already wins.

| profile | what it models | score |
|---|---|---|
| `fanout_naive` | one-shot completion per (aircraft, AD) pair, no cross-item state — literally what `b1b7`'s agent ran (`worker.py` + ThreadPool) | **10/14 = 0.71** |
| `fanout_smart` | 162 independent extraction calls, then determinations + policy + the whole coherence layer computed deterministically in Python | **13/14 = 0.93** |
| `serial_sa_35pct` | honest serial single agent that runs out of budget at 35% coverage | **4/14 = 0.29** |
| `swarm_good` | complete, coherent, correct submission (the ceiling) | **13/14 = 0.93** |

**`fanout_smart` == `swarm_good`. The gap is exactly 0.00.** Even the cheapest attack clears the
0.40 ceiling by 31 points.

## 3. Why — and why this is not a fixable flaw in this particular rubric

Every check in the rubric turned out to be one of exactly two kinds:

- **Per-item** (register coverage, effective dates, supersession status, models named, verbatim
  applicability quotes, serial-in-list resolution, condition-quote grounding). Independent per
  document. This is the shape `b1b7` already proved fan-out eats.
- **Structural / cross-item** (rule ids resolve, every rule invoked, class consistency, summary
  reconciles, no superseded AD marked applicable). These *look* like coordination checks, but a
  script satisfies them **by construction** — it computes the classes, assigns rule ids, and is
  therefore perfectly consistent, more reliably than any agent.

The only profile that scores low is the honest serial agent, and it scores low purely on
**coverage** — which is exactly the thing a $1 fan-out buys.

I also worked through, and rejected, the obvious hardenings:

- *Require retroactive revision when a later AD supersedes an earlier one.* A script computes
  supersession up front and simply never makes the superseded determinations. Penalising that is
  penalising the better method, and a "revision" obligation with no required population is
  vacuously satisfiable — the coverage-blind-denominator trap in reverse.
- *Require an inductively-built policy with amendments.* Same problem: an agent that reads all
  instances before writing the rule needs no amendment. Requiring one is process-prescriptive
  and would be a manufactured gap.
- *Make the per-unit input require multi-hop retrieval.* The closure over `AD YYYY-NN-NN`
  cross-references is regex-computable; a two-hop prompt is ~36k chars, still one completion.

## 4. The generalisation (this is the part worth keeping)

`b1b7` concluded "any task that decomposes into *generate candidates cheaply, then judge each
candidate independently* is fan-out-able." This test extends that:

> **A cross-item obligation only resists fan-out if the state it carries cannot be reconstructed
> by a script.** If the carried state is compact and structured — a set of ids, a resolved graph,
> a condition-class index, a running budget — the single agent extracts it with independent calls
> and then satisfies every consistency, precedent and reconciliation obligation *deterministically
> in Python*, more reliably than an agent does. Consistency checks, precedent-citation checks and
> rollup-reconciliation checks are therefore **not** coordination measurements. They are free
> points for a scripted attacker.

Restated as a screening question to apply before building: *could I satisfy this check with a
`for` loop over extracted fields?* If yes, it measures nothing about coordination.

Corroborating evidence that this is systemic rather than a property of one design: across every
run in this workspace's `mascloud runs` history, no task has reached the 0.23 gap floor —
`be59` peaked at MA 0.787 / SA 0.66, `a947` at MA 0.784 / SA 0.723, `b1b7` at SA ~0.85. The
single historical 0.30 gap came from a stacked depth band with graduated cutoffs, and that was
rejected by the client as post-hoc calibration (LESSONS LOG, 2026-07-13).

## 4a. Premise test 2 — "shared mutable state under contention" also fails

Section 5 below originally nominated contention as the one surviving shape. It was then tested
with the same harness (`premise_test_contention.py`, same frozen corpus): 20 airframes competing
for 40 weekly maintenance-line slots, demand exactly saturating supply so ordering decides who is
deferred, deadlines derived from each AD's real effective date plus the compliance interval quoted
from its own text.

| profile | score |
|---|---|
| cheap one-shot fan-out (each worker plans one airframe, blind to the shared line) | 5/7 = 0.71 |
| scripted fan-out (extraction calls, then a Python solver over the extracted deadlines) | **7/7 = 1.00** |
| honest serial single agent at 35% coverage | 5/7 = 0.71 |
| ideal swarm | **7/7 = 1.00** |

**Gap versus a scripted attacker: 0.00 again.** A ~30-line deadline-sorted greedy allocator
satisfies every contention obligation — no double booking, capacity respected, deadline ordering,
deferrals citing the commitment that consumed the capacity.

Two further lessons fell out of it:

- **Contention checks are coverage-blind by construction.** "No double booking" and "capacity
  respected" are *easiest* to satisfy by booking almost nothing — which is why the truncated
  serial agent also scores 0.71 here, matching the cheap fan-out. This is the
  coverage-blind-denominator trap (kickstart section 5) arriving through the front door.
- The shape separates only the **cheap** attacker (+0.29), not the competent one.

## 4b. The result stated formally

Both arms are programs with LLM-oracle access, running in the same container, with the same
credential, the same shell and the same tools. Their *computational* capability is therefore
identical: any function the swarm can compute, a script in the single-agent container can compute.
What differs is only

1. **behaviour** — whether the agent in fact organises the work well, and
2. **wall-clock**, which for long-horizon tasks is uncapped for both.

So under the current configuration the benchmark cannot measure a *capability* gap. It can
measure a *behavioural* gap — and the two premise tests bracket exactly how wide that is:
**0.00 against a competent scripted attacker, +0.29 against a naive one.** Which of those a live
run reports depends on whether that particular agent bothered to write the script. `b1b7`'s agent
went looking for the credential on its **second shell command of the run**.

## 5. What was nominated as surviving (now disproven — see 4a)

On this analysis the only remaining shape where a fan-out is *actively harmful* rather than
merely equivalent is **shared mutable state under contention**: units of work that act on one
stateful system whose state lives outside any prompt, so that uncoordinated parallel action
produces detectable conflicts, and correctness requires partitioning access. A script can
serialise to stay correct, but then it buys no parallelism; a swarm that partitions correctly
does. That measures coordination-under-contention, which is the capability the benchmark is
actually named for.

The alternative is that no durable gap exists until the platform withholds the inference
credential — which is precisely what
`ESCALATION - Single agent self-parallelisation via injected OPENAI_API_KEY.md` asks for. This
finding is a **second, independent, quantified data point for that escalation**: a different
domain, a different corpus, a different rubric, the same result, obtained without spending a
cloud run.

## 6. Reusable output

`premise_test.py` is a corpus-grounded screening harness, not a one-off. It recomputes every
expectation from the frozen input (no oracle), defines the rubric as executable boolean checks,
synthesises four submission profiles including two fan-out attacks, and prints the per-check
matrix. Point it at the next candidate design **before** writing `instruction.md`. Killing this
design cost zero cloud runs.
