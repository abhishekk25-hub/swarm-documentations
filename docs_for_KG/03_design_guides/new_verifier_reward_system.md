G A P N O T A C H I E V E D
Five RCAs, five tasks, zero gaps
TA S K 	S I N G L E A G E N T 	M U LT I A G E N T 	G A P
Task 1 	0.5515 	0.6667 	0.115
Task 2 	0.339 	0.50 	0.16
Task 3 	0.4062 	0.0 crashed 	n/a
Task 4 	0.5469 	0.506 	−0.04
Task 5 	0.4467 	0.5834 	0.137
Floor is 0.20. Nobody cleared it, and two tasks moved the wrong way after a deliberate fix. That is
not five bad-luck stories, it is one shared design error.

-- 12 of 19 --

G A P N O T A C H I E V E D
The single agent starts from a high floor
If roughly half the reward is reachable by a submission that is complete, schema-valid and lexically
derived from the source, then an agent that reads nothing already banks 0.5 and there is no room
above it for a 0.20 gap.
Averaging a saturated structural half with a floored judged half lands every competent submission
near 0.5. The scoring architecture, not the task, is what fails to express the gap.

-- 13 of 19 --

G A P N O T A C H I E V E D
An agent that did nothing should not score half
While every check is worth the same, a handful of file-existence checks is a large share of the
reward. That is how a submission with no real work still lands near 0.5.
file A exists
file B exists
file C exists
output.json parses
Four checks, four equal points, awarded for producing empty shells. On a ten-check rubric that is 40 percent before any work happens.
G U I D A N C E F R O M M A N A G E M E N T : P O I N T VA L U E B Y C H E C K T Y P E
1 pt
Structure check
Files exist, parse, match the schema, columns and enums
are valid.
2 pts
Reward-hacking check
Catches gaming: templating, near-duplicates, fabricated
evidence, uniform filler, degenerate submissions.
3 pts
Partial oracle check
Is the answer actually right: accuracy and recall against
real ground truth, grounded evidence, judged depth.
W H Y T H I S WO R KS
Nothing is worth more than 3 points, and reward is passed points over total possible points. The structural layer's share of the total drops on its own, without removing any
checks, so completeness alone can no longer carry a submission and the real work is where the points are.

-- 14 of 19 --

P O I N T W E I G H T S
What it does to the score
Take five checks in each category, and assume the structural ones mostly pass, because
they usually do.
C AT E G O R Y 	W E I G H T 	PA S S E D T E S T S
Structure 	1 	4 of 5
Reward hacking 	2 	1 of 5
Partial oracle 	3 	1 of 5
score = sum(passed tests × weight) / sum(total tests × weight)
W I T H N O W E I G H T S
passed = 1 + 1 + 4 	= 6
total = 5 + 5 + 5 	= 15
score = 6 / 15 	= 40%
Structure contributes roughly 27 percent of the final score, 4 of the 15 possible points.
W I T H W E I G H T E D P O I N T S
passed = 1×2 + 1×3 + 4×1 = 9
total = 5×2 + 5×3 + 5×1 = 30
score = 9 / 30 	= 30%
Structure contributes roughly 13 percent, 4 of the 30 possible weighted points.
S A M E S U B M I S S I O N , S A M E C H E C KS
The score drops from 40 to 30 percent and the structural share halves, purely because the structural pass is no longer carrying the result. Nothing was removed and
nothing was made stricter.

-- 15 of 19 --

D O N ' T C H A S E T H E G A P
What chasing looks like, and why it fails
C H A S I N G 	W H AT AC T U A L LY H A P P E N E D
I N O N E L I N E
A check that costs both arms equally does not move the gap. Never spend an iteration on a check whose effect is smaller than normal run-to-run variance.
Harden the one judge that is scoring too generously.
Reweight reward off the oracle and onto the judged checks.
Add a check to catch the specific thing SA did last run.
Add more sub-agent roles and hope MA climbs.
A judge was hardened from 0.875 to 0.000 on SA exactly as designed. SA's total
went up 0.057, because run-to-run variance on other axes was larger than the
check removed.
Reward was moved off the oracle onto judged narrative depth. Both arms dropped
by the same amount. Gap unchanged.

-- 16 of 19 --

D O T H I S I N S T E A D
Same model on both sides
The single agent and the multi agent run the same model, so the same intelligence is on both sides
of the comparison. Adding more tests does not make the single agent fail, it just lowers both scores
by the same amount.
D O E S N O T C R E AT E A G A P
More checks. Stricter checks. A harsher judge. Anything that makes the rubric tougher
is paid for equally by both arms, so the difference between them stays exactly where it
was.
C R E AT E S A G A P
A genuinely more complex task, one that a single context cannot hold at quality, plus a
decomposition that lets the swarm actually split it. The decomposition is where the
multi agent's benefit comes from, so that is where the effort belongs.
S O
If the gap is short, the answer is a harder task and a better decomposition.yaml, not a stricter verifier.

-- 17 of 19 --

D E M O
Read the trajectories
Read what the model actually did, on the failed runs as well as the final ones. Use harbor view
rather than grepping raw JSON.