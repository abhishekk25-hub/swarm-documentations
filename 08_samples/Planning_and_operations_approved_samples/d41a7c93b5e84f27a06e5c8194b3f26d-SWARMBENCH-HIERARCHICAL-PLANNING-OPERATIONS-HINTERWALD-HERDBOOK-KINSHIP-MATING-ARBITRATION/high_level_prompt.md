I need the 2010 Hinterwälder mating round ready for the breeding committee on 1 March. Everything is in `/input_artifacts`; the charter there governs how the round is worked and beats general practice wherever the two differ. Outputs go in `/logs/agent`.

A hundred living animals, eighteen member holdings, fourteen free breeding places. Two things will slow you down: the pedigree is a real herdbook extract with real gaps and inconsistencies in it, and the vet notes are free-written and contradict each other — restrictions placed, lifted, replaced, some already expired, some written at visits that fall after the round opens. Each restriction on an animal has to be settled separately.

Six deliverables.

`kinship_register.csv`: every living animal, with its inbreeding coefficient, mean kinship, conservation priority rank, founder share, breeding standing, the restrictions actually standing on the round date, and a word-for-word quote of the statement that settles its breeding standing.

`mating_allocations.csv`: the matings the round commits, with pair kinship, expected progeny inbreeding, host holding, the animal each one actually displaced, and why.

`movement_plan.csv`: every movement the round creates, with certificate class, transport category, receiving isolation and the capacity left at the far end.

`board_conflicts.csv`: every animal the charter counts as a conflict, with the genetics, veterinary and movement position on that specific animal, the constraint that actually bound, and how it was arbitrated.

`herd_dashboard.html`: one self-contained page — conservation priority across the herd drawn rather than tabulated, the allocations, and where the conflicts sit. Every animal gets its own visible mark. Embed the underlying tables as JSON so the screen matches the files.

`conservation_plan.md`: 1,800–3,200 words under the headings named in `instruction.md`, including a control-totals table, animals discussed by ear tag against facts the record confirms, and a defence of every allocation.

Exact column lists and the control-total keys are in `instruction.md`. The six must agree with each other, and all six must exist at those paths when you stop.
