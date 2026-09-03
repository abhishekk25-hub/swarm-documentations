# Hinterwälder Conservation Herdbook — 2010 Mating Round Charter

Working conventions adopted by the breeding committee for the 2010 round. These are this
programme's own rules for this exercise. They are not a restatement of any regulator's
requirements, and where general practice would say something different, this charter
governs.

**Round date: 1 March 2010.** Every age, standing and eligibility question in this round
is settled as at that date and no other.

---

## 1. Relatedness

### 1.1 Unknown ancestry

`herdbook_pedigree.csv` carries the herdbook as it stands, including its gaps. Where a
`sire_id` or `dam_id` is blank, or names an animal that has no record of its own in the
file, that parent position is an **unknown founder**: unrelated to every other animal in
the herdbook and not itself inbred. Every such position is a separate founder. Two blanks
are never the same animal, even in the same record.

The extract also carries a small number of internal inconsistencies of the kind
pedigree-checking tools are built to catch. One animal is recorded as female and is
nonetheless used in the sire position of four records, and 24 historic ancestors carry no
birth year at all. **Relatedness follows the parent links as recorded.** The `sex` field
governs only which side of a mating an animal may take; it never changes who its parents
are, and a missing birth year never removes a record from the pedigree. Where a cohort
range is used to divide the pedigree up for reading, records with no birth year belong
with the earliest range.

### 1.2 Kinship

Kinship `f(i,j)` is the probability that an allele drawn at random from `i` and one drawn
from the same locus in `j` are identical by descent. Compute it by the tabular method over
the whole herdbook, working in an order that places both parents before their offspring:

- `f(i,i) = 0.5 * (1 + F(i))`, where `F(i)` is the inbreeding coefficient of `i`
- `f(i,j) = 0.5 * (f(sire(i), j) + f(dam(i), j))`, where `i` is the later of the two
- `F(i) = f(sire(i), dam(i))`, and `F(i) = 0` for any unknown-founder position

### 1.3 Mean kinship

`MK(i)` is the arithmetic mean of `f(i,j)` over **every living animal `j` in the herdbook,
including `i` itself**. Animals recorded `HISTORIC` shape the relatedness that the
pedigree determines but are not in this mean and not in its denominator.

`mk_rank` orders living animals by ascending `MK`: rank 1 is the lowest mean kinship and
so the highest conservation priority. **Ties break by ascending `animal_id`.** Ranks run 1
to 100 with no gaps and no shared ranks.

### 1.4 Founder share

`founder_share` is the proportion of an animal's genome descending from each founder
position: a founder contributes `1.0` to itself, and every other animal takes
`0.5 x (sire's share) + 0.5 x (dam's share)`. Report it as a pipe-separated list of
`<founder>:<proportion>` items covering every founder with a non-zero share, ordered by
descending proportion then by ascending founder label, proportions to four decimal places.

Naming a founder, which the reporting has to be consistent about:

- A record with **neither** parent recorded is a founder in its own right and is named by
  its own `animal_id`. Its two blank positions stay unrelated to everything else, exactly
  as 1.1 says, so this changes no kinship or inbreeding figure; it is only the label the
  share is reported under.
- A record with **one** parent recorded and the other blank or unresolvable takes the
  known parent's founders through that side, and the missing side is a founder of its own
  labelled `<animal_id>:SIRE` or `<animal_id>:DAM` after the record that carries it.
- A `sire_id` or `dam_id` naming an animal with no record of its own is an unresolvable
  position, not an ancestor. It is labelled after the record that carries it in the same
  way, and two records naming the same absent parent do **not** share a founder.

---

## 2. Standing of an individual

### 2.1 Age class

Age is `2010 minus birth_year`. `YOUNGSTOCK` is under 2; `BREEDING_AGE` is 2 to 12
inclusive; `AGED` is over 12.

### 2.2 Reading the herd health correspondence

Each living animal is discussed in the file of the holding that keeps it. The files are
ordinary visit notes written by the attending vet, filed in visit order. There is no fixed
wording: a vet may place a restriction, lift one, or simply record an observation, in
whatever words they chose on the day.

A restriction stands on the round date when, and only when, all of the following hold for
that animal and that restriction:

1. Statements made at a visit **after** the round date are disregarded entirely. A recheck
   already booked for April decides nothing about where the animal stands in March.
2. Among the remaining statements bearing on that restriction, only the one from the
   **latest visit** governs. An earlier statement never survives a later one, in either
   direction: a restriction lifted in the autumn and placed again in January stands, and
   one placed in the autumn and lifted in January does not.
3. That governing statement places the restriction rather than lifting it.
4. Any end date it names has not already passed. A restriction written to run to a date
   before 1 March 2010 lapsed on its own terms.

An observation that places or lifts nothing — a routine check, a weighing, a trim — is not
a statement about any restriction.

The restrictions this round recognises are:

| restriction | effect |
| --- | --- |
| `BREEDING_BLOCK` | the animal may not be entered for service |
| `ISOLATION_ONLY` | the animal must be kept singly, and may not be entered for service |
| `MOVEMENT_BLOCK` | the animal may not be transported |
| `EXTENDED_ISOLATION` | adds the stated number of days to any receiving isolation |
| `MATING_EXCLUSION` | the animal may not be mated to the specific animal named |

Each is settled separately, and a `MATING_EXCLUSION` is settled separately for each animal
named. An animal may be clear to breed and still unfit to travel.

A `MATING_EXCLUSION` binds only where the animal it names is itself in the living herd.
Where the named partner is not a living animal, the exclusion cannot rule out any mating
this round can make, and it is not a constraint on the round.

### 2.3 Breeding status

Apply in order and stop at the first that matches:

| order | status | condition |
| --- | --- | --- |
| 1 | `INELIGIBLE_AGE` | age class is not `BREEDING_AGE` |
| 2 | `HELD_HEALTH` | a `BREEDING_BLOCK` or an `ISOLATION_ONLY` restriction stands |
| 3 | `RESTED` | a cow whose 2009 rows in `previous_matings.csv` total two or more calvings |
| 4 | `ELIGIBLE` | none of the above |

A `MOVEMENT_BLOCK` does not affect breeding status. It prevents the animal travelling.

---

## 3. Mating allocations

An allocation may be recommended only where all of the following hold:

- one `ELIGIBLE` cow and one `ELIGIBLE` bull
- `f(cow, bull) < 0.03125`
- neither carries a `MATING_EXCLUSION` standing against the other
- the two are not recorded as `FAILED` together twice or more in `previous_matings.csv`
- the host holding is the **cow's** own holding; cows are not moved for service
- each cow appears in at most one allocation

Expected progeny inbreeding is the kinship of the two parents.

**Sire contribution.** A bull may be allocated to **at most two cows**, and where he takes
two, both cows must be at the same holding — a bull travels to one holding for the season
and no further.

**Places.** A holding's free breeding places are
`breeding_places - breeding_places_occupied`. Allocations hosted at a holding may not
exceed that figure. Fourteen places are free across the membership, so the round cannot
exceed fourteen allocations.

**Breeding values.** `breeding_value` in the herdbook is the programme's published index
for the trait it records. It carries no constraint in this charter: it is context for the
committee's judgement, not a rule, and an allocation is never invalid on account of it.

---

## 4. Movements

### 4.1 What the round obliges

- **`SIRE_PLACEMENT`** — where an allocated bull is not already at the host holding, he
  moves there. One movement per bull however many cows he covers; a bull already resident
  generates none. A bull under a standing `MOVEMENT_BLOCK` cannot travel, so an allocation
  requiring him to move is not available.
- **`ISOLATION_RELIEF`** — a holding whose `isolation_boxes_occupied` exceeds its
  `isolation_boxes` is over-committed. Each animal it keeps under a standing
  `ISOLATION_ONLY` must move to a holding with a free isolation box, unless that animal is
  itself under a standing `MOVEMENT_BLOCK`.

### 4.2 Deriving a movement's attributes

- **`certificate_class`** — by whether the consigning and receiving countries differ, per
  `movement_rules.csv`.
- **`transport_category`** — from the animal's **most recent** row in
  `weight_records.csv`, against the liveweight bands in `movement_rules.csv`.
- **`isolation_days`** — the base band for the receiving holding's health status and
  whether the movement crosses a border, **plus** any days carried by an
  `EXTENDED_ISOLATION` standing for that animal.
- **`arrival_capacity_after`** — places of the relevant kind left at the receiving holding
  once every movement in this round is counted: free **breeding** places less allocations
  hosted there for a `SIRE_PLACEMENT`, free **isolation** boxes less relief arrivals there
  for an `ISOLATION_RELIEF`. It may not be negative.

---

## 5. Conflicts

The three review boards work from different evidence and will not agree. A **conflict** is
recorded for every animal in the top quartile of conservation priority — `mk_rank` of 25
or better — that the round does not place in any allocation. Its `binding_constraint` is
the first of these that applies:

| code | meaning |
| --- | --- |
| `AGE` | breeding status is `INELIGIBLE_AGE` |
| `HEALTH_BLOCK` | breeding status is `HELD_HEALTH` |
| `RESTED` | breeding status is `RESTED` |
| `NO_ELIGIBLE_PARTNER` | eligible, but no animal of the other sex clears the kinship ceiling, the exclusions and the twice-failed rule |
| `MOVEMENT_BLOCK` | such partners exist, but every one of them would need a movement a standing `MOVEMENT_BLOCK` forbids |
| `NO_PLACE` | a workable partner existed and the round spent the place elsewhere |

### 5.1 Recording a conflict

Each board's position is written about **that animal**, in sentences, naming its ear tag
and the figure the board is arguing from; a status word repeated down the column is not a
position and records nothing the register does not already carry.

The genetics position is a comparison, because conservation priority is only ever relative:
name the animal this one lost the place to, or the nearest animal it was measured against,
and give **that** animal's mean kinship beside this one's, both to the decimals set out in
section 6. A position that reports only the animal's own figures states a rank without
stating what it was ranked against.

The `resolution_note` records what actually settled the round for this animal: the partner
that was ruled out, the holding that had no place left, the calvings behind a rest year, or
the age it reached this spring, according to which constraint bound.

---

## 6. Reporting conventions

Kinship, mean kinship, pair kinship and expected progeny inbreeding are reported to **five
decimal places**; inbreeding coefficients and founder shares to **four**. Round half away
from zero. Holdings are named by `holding_code`. Where a field does not apply to a row,
leave it empty rather than writing a dash or a zero, except where the column's own
vocabulary supplies a `none` value.
