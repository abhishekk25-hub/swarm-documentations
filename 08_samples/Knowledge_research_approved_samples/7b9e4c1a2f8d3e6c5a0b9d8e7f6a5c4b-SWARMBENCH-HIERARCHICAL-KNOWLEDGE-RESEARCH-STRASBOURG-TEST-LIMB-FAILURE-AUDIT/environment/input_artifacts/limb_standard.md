# Limb coding standard

This is the standard our unit codes case-law to. It fixes the vocabulary, the field contract for every
deliverable, and the rules for the derived fields. Follow it literally: the review pipeline reads these
files without a human in between.

## 1. What a finding is

A **finding** is one merits ruling in a judgment's operative provisions - one item beginning `Holds`
that says there has or has not been a violation of a named Convention article.

- A ruling on just satisfaction (Article 41), on admissibility (`Declares`), on joining applications
  (`Decides`), or on the remainder of a claim (`Dismisses`) is **not** a finding and is never coded.
- Where one operative item names two articles jointly - "a violation of Articles 3 and 8" - that is
  **two findings**, one per article, each coded on its own.
- Where an operative item names one article **in conjunction with** another - "a violation of Article 13
  in conjunction with Article 6 § 1" - that is **one finding**. The article coded is the one whose
  violation is held (Article 13 in that example); the other is recorded in `conjoined_with`.
- A finding is coded whether the outcome is a violation or no violation. A no-violation finding is
  coded on the same terms: the Court still applied the test, and which limb the State satisfied is
  exactly as informative as which limb it failed.

## 2. The limb vocabulary

Every finding belongs to one **family**, fixed by its article. Each family has a closed set of **limb
codes**. No other code may appear anywhere in any deliverable.

| Family | Articles | Limb codes |
| :--- | :--- | :--- |
| `LIFE` | 2 | `A2-SUB`, `A2-PROC` |
| `ILLTREATMENT` | 3 | `A3-SUB`, `A3-PROC` |
| `LIBERTY` | 5 | `A5-GROUNDS`, `A5-PROMPT`, `A5-REVIEW`, `A5-COMPENSATION` |
| `FAIRTRIAL` | 6 | `A6-ACCESS`, `A6-TRIBUNAL`, `A6-ADVERSARIAL`, `A6-REASONS`, `A6-LENGTH`, `A6-PUBLICITY`, `A6-PRESUMPTION`, `A6-DEFENCE` |
| `QUALIFIED` | 8, 10, 11, and Article 1 of Protocol No. 1 | `QR-LEGALITY`, `QR-AIM`, `QR-NECESSITY`, `QR-POSITIVE` |
| `REMEDY` | 13 | `A13-EXISTENCE`, `A13-EFFECTIVENESS` |
| `DISCRIMINATION` | 14 | `A14-COMPARATOR`, `A14-DIFFERENCE`, `A14-JUSTIFICATION` |
| `MISUSE` | 18 | `A18-PURPOSE` |
| `ELECTIONS` | Article 3 of Protocol No. 1 | `P13-CONDITIONS` |

What each code means:

- `A2-SUB` / `A3-SUB` - the State's own agents or its failure to protect caused the death or the
  ill-treatment. `A2-PROC` / `A3-PROC` - the investigation the State owed afterwards was inadequate,
  whatever the substantive position.
- `A5-GROUNDS` - the detention did not fall within a permitted ground, or was not lawful, under
  Article 5 § 1. `A5-PROMPT` - Article 5 § 3, being brought promptly before a judge or the length of
  pre-trial detention. `A5-REVIEW` - Article 5 § 4, the review of lawfulness.
  `A5-COMPENSATION` - Article 5 § 5.
- `A6-ACCESS` - access to a court at all. `A6-TRIBUNAL` - independence, impartiality, or a tribunal
  established by law. `A6-ADVERSARIAL` - equality of arms, disclosure, the handling of evidence or
  witnesses. `A6-REASONS` - the domestic court's failure to give reasons or to address an argument.
  `A6-LENGTH` - the length of proceedings. `A6-PUBLICITY` - a public hearing or public pronouncement.
  `A6-PRESUMPTION` - Article 6 § 2. `A6-DEFENCE` - the Article 6 § 3 defence rights.
- `QR-LEGALITY` - the interference was not in accordance with the law, prescribed by law, or lawful.
  `QR-AIM` - it pursued no legitimate aim, or none of those relied on. `QR-NECESSITY` - it was not
  necessary in a democratic society, or, for Article 1 of Protocol No. 1, did not strike a fair
  balance. `QR-POSITIVE` - the case was not analysed as an interference at all but as a positive
  obligation, and turned on the adequacy of what the State did to protect the right.
- `A13-EXISTENCE` - no remedy existed. `A13-EFFECTIVENESS` - a remedy existed but was not effective
  in practice.
- `A14-COMPARATOR` - whether the applicant was in a relevantly similar situation to the comparator.
  `A14-DIFFERENCE` - whether there was a difference in treatment at all. `A14-JUSTIFICATION` -
  whether the difference had an objective and reasonable justification.
- `A18-PURPOSE` - whether the restriction pursued an ulterior purpose.
- `P13-CONDITIONS` - whether the conditions imposed impaired the free expression of the opinion of
  the people.

## 3. Coding a finding

For every limb code in the finding's family, record exactly one verdict:

- `failed` - the Court held this limb was not satisfied. On a violation finding, at least one limb is
  `failed`. On a no-violation finding, no limb is `failed`.
- `satisfied` - the Court expressly held this limb was met, or expressly proceeded on the footing that
  it was met, and said so.
- `not_examined` - the Court did not decide this limb: it said so, or it disposed of the case on
  another limb and never reached this one. A limb the judgment simply never mentions is
  `not_examined`, not `satisfied`.

`decisive_limb` is the single limb code the finding actually turned on. On a violation finding it is a
limb you marked `failed`; where two limbs failed, it is the one the Court reached first in its
assessment. On a no-violation finding it is the limb the Court examined last and answered in the
State's favour - the one that would have decided the case the other way.

**The distinction the review exists to draw.** A judgment that recites that an interference was lawful
and pursued a legitimate aim, and then finds against the State on proportionality, has one failed limb,
not three. Words from a limb's vocabulary appearing in a judgment are not that limb failing. Code what
the Court held, not what it mentioned.

## 4. Field contract - `/logs/agent/findings/<case_id>.json`

One file per judgment, named by its `case_id`, a JSON object with exactly these keys:

- `case_id` - string, the judgment's identifier, matching the file name.
- `respondent_state` - string, exactly as `respondent_states.json` spells it.
- `findings` - a list, one object per finding in that judgment's operative provisions, in the order the
  operative provisions give them. Each object has exactly these keys:
  - `finding_id` - string, `F-<case_id>-NN`, NN counting from 01 within the judgment.
  - `article` - string, the article token: a plain number for a Convention article (`6`, `8`), or
    `P<protocol>-<article>` for a Protocol article (`P1-1` for Article 1 of Protocol No. 1).
  - `family` - string, one of the nine family names in section 2.
  - `outcome` - string, `violation` or `no_violation`.
  - `conjoined_with` - string, the article token this finding was held in conjunction with, or the
    empty string.
  - `limb_verdicts` - an object with one key per limb code in the family, and no other keys, each
    value one of `failed`, `satisfied`, `not_examined`.
  - `decisive_limb` - string, one limb code from the family.
  - `paragraph_no` - integer, the numbered paragraph of the judgment carrying the sentence in which the
    Court states the decisive limb's outcome.
  - `quote` - string, at least 15 words of the Court's own wording from that paragraph, copied exactly,
    stating that outcome. It must come from the Court's assessment - after `THE LAW` and before the
    operative provisions - and be a quotation, not a paraphrase.
  - `turning_point` - string, 25 to 60 words in your own words: what the case turned on at that limb.
    Name the thing this judgment holds that its siblings do not - the safeguard that was absent, the
    material the domestic court refused to consider, the reason the State's justification failed or
    held. An article number, the respondent State, or a restatement of the limb code's own definition
    names nothing.

## 5. Field contract - `/logs/agent/limb_matrix.csv`

A UTF-8 CSV, header row, these six columns in this order:

`limb_code,family,findings,states_touched,failed_count,lead_case_id`

One row for every limb code that is the `decisive_limb` of at least one finding anywhere in the review,
and no row for any other code. `findings` is how many findings across the corpus have that code as
their `decisive_limb`; `states_touched` is how many of the 10 States have at least one such finding;
`failed_count` is how many of those findings have `failed` as that limb's verdict; `lead_case_id` is the
`case_id` of the case with the most such findings, ties broken by `case_id` ascending as text. Sort by
`findings` descending, ties by `limb_code` ascending as text.

## 6. Field contract - `/logs/agent/state_profile.csv`

A UTF-8 CSV, header row, these six columns in this order:

`respondent_state,slug,findings,violations,dominant_limb,pattern`

Exactly 10 rows, one per State in `respondent_states.json`, `respondent_state` and `slug` copied from
it. `findings` is how many findings that State's four judgments produced; `violations` how many are
`violation`. `dominant_limb` is the limb code that is `decisive_limb` in the most of that State's
findings, ties broken by `limb_code` ascending as text. `pattern` is 25 to 60 words in your own words:
what the State's four judgments have in common at the limb level, named concretely enough that a reader
can see it is the same failing twice. Where nothing recurs, say so and say what the four have instead.

## 7. Field contract - `/logs/agent/limb_brief.md`

A markdown brief of a few hundred words with a level-1 heading and exactly these three level-2 sections,
in this order and no others:

- `## Where the States are losing` - which limbs carry the adverse findings across the corpus.
- `## Procedure against substance` - what the split between procedural and substantive limbs shows.
- `## What to put right first` - the limb a ministry should act on, and why that one.

Every figure in the brief must be one you can derive from your own deliverables.

## 8. Constraints on the finished review

The finished set has to satisfy all of these:

1. One findings file per judgment, forty in all.
2. Every finding in a file is a merits ruling in that judgment's operative provisions, and every such
   ruling has a finding.
3. Every `limb_verdicts` object carries exactly the limb codes of its family, no more and no fewer.
4. Every violation finding has at least one `failed` limb; no no-violation finding has any.
5. `decisive_limb` is always a code from the finding's own family.
6. No two findings anywhere in the review carry the same `quote`.
7. `limb_matrix.csv` and `state_profile.csv` count what the findings files actually carry.
