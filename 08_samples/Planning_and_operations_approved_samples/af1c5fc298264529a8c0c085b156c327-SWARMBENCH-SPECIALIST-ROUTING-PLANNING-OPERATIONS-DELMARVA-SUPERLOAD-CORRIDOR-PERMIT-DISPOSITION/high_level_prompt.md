# High-level request

Clear the spring 2026 superload docket. Seventy-two applications, six heavy-haul corridors,
eighty-eight structures, and twenty engineer-weeks of load-rating time to spend.

Everything you need is under `/input_artifacts/`: the pinned bridge extract, the rules in force,
the corridor definitions, the applications, the district field memos, the engineer roster and the
source manifest. Nothing is fetched.

Put seven files at these exact absolute paths:

- `/logs/agent/structure_capacity_register.csv`: one row per structure, what it can carry today.
- `/logs/agent/permit_dispositions.json`: the decision on each application, with its path, its
  controlling structure, its conditions and its escort class.
- `/logs/agent/rerating_programme.csv`: which structures get re-rated, by whom, in which week,
  and which applications that frees.
- `/logs/agent/corridor_bottleneck_ledger.tsv`: thirty rows, each corridor against each weight
  band.
- `/logs/agent/refusal_register.csv`: one row per application not issued, with the reason and
  whether re-rating would fix it.
- `/logs/agent/capacity_profile.svg`: the corridor capacity chart, standalone, no external files.
- `/logs/agent/permit_decision_letter.md`: a docket summary and one section per application.

The seven files describe one docket and must agree with each other on every identifier, figure and
count. Use only identifiers that appear in the packaged records, and only criteria the rules file
states. Do not assess a structure twice or dispose an application twice. The programme must fit
inside the twenty engineer-weeks and the eight-week window. Write each letter section from its own
case. Repeated boilerplate with the names swapped is not a decision letter.
