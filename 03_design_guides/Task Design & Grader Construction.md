Task Design & Grader Construction

Following up on the verifier examples above, the client also sent over deep-dive feedback on Task Design and Score Construction.

The main takeaway: The client wants us to reward substance over shape. A perfectly formatted but empty file shouldn’t get a high score.

The client explicitly praised the following tasks as the gold standard for how tasks should be structured and graded:

1. 911-COMMISSION-BRIEFING-DECK
Why the client loved it: Praised as "one of the strongest task designs in the batch."
The Takeaway: Instead of a simple sweep across repos, the agent has to read a massive 1.65-million token report and synthesize it into a single, highly-constrained slide deck. This is exactly the kind of "read everything, then build" structural complexity they want to see.

2. SEC-EDGAR-ANSWER-AUDIT & GLEN-HELEN-BID-NOTICE-AUDIT
Why the client loved it: Both were called "exemplars" for their use of Ground Truth.
The Takeaway: Both use tight-tolerance deterministic checks based on actual, frozen ground truth rather than relying heavily on LLM judges. The client wants to see ground truth checks denominated over the whole corpus wherever possible.

3. RECOVERY-TRIAL-PUBLIC-RECORD-AUDIT
Why the client loved it: Called "the best-composed grader in the batch."
The Takeaway: It has a near-zero "freebie floor" (~1%). 99% of its checks are substantive content checks. An agent gets zero points just for creating files with the right schemas - it has to actually do the work.

4. WORLD-BANK-DEVELOPMENT-ECONOMICS / US-VETERANS-CLAIMS
Why the client loved it: Both were praised as "exemplars for the authorship gate."
The Takeaway: They put all per-record checks behind an _eligible gate (checking copy-density, word-order, etc.). If the agent just copied/pasted or wrote a hollow file, the gate fails it immediately, scoring a flat zero.

Action Items for New Tasks:
1. Kill the "Freebie Floor": Stop giving out lots of points just because a file exists, has the right columns, or copies an ID over.
2. 40% Content Rule: Going forward, the client requested that at least 40% of every grader's score must come from content (rubric + ground truth), not structural checks.

Let's make sure we are leaning into these "Floor-Killers" and complex synthesis patterns!