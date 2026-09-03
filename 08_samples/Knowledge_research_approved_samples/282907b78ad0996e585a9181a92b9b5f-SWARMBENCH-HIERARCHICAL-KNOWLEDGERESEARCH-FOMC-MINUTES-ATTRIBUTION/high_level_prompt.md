Resolve the hedged attributions in the 2020 FOMC minutes against the verbatim meeting
transcripts.

The supplied claims file lists 183 claims drawn from eight 2020 meetings. Each one reports that
some unnamed subset of participants held a view, in the form the minutes use, such as a few
participants, several participants, or a majority of participants. The transcripts and the
minutes for all eight meetings are supplied as text.

For each claim in the file, produce a JSON record under the claim records directory named by its
claim id. Every record must carry the claim id, the meeting date, a roster and a counterpoints
list.

The roster names the participants whose remarks at that meeting express the claim. Each entry
carries the participant surname and one quotation copied exactly from that participant's remarks
at that meeting.

The counterpoints list has the same shape and names participants at that meeting who argued
against the claim. An empty counterpoints list is acceptable where nobody did.

Attendance lists in the minutes distinguish participants from staff. Staff remarks do not belong
in either list.

Quotations must be contiguous and exact, taken from the speaker they are attributed to, and
drawn from the passage that actually carries the view rather than an unrelated passage using
similar words.

Also produce an attribution matrix as CSV. Claims form the rows, every participant named
anywhere in the rosters forms the columns, and each cell records whether that participant was
placed on that claim. The matrix must be consistent with the records.

Deliverables are the per claim JSON records and the attribution matrix CSV, both written to the
specified output paths.
