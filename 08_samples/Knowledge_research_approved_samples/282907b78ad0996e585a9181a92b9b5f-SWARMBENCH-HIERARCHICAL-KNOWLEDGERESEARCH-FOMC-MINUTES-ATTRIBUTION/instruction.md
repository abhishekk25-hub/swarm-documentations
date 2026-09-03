I research central bank communication, and I am writing a paper on how faithfully the Federal
Open Market Committee minutes describe what was actually said in the room. The 2020 meeting
transcripts came out of their five year embargo this January, so for the first time the 2020
minutes can be checked against the verbatim record. I need that check done claim by claim, and I
need to be able to defend every attribution in the paper to a referee who will look up the
transcript himself.

The minutes never name anyone. They say things like "several participants noted" or "a couple of
participants remarked". I want to know who those participants were in each case, in their own
words, and I also want to know who was arguing the other way, because that is the part a summary
tends to lose.

Here is what I am giving you.

/input_artifacts/claims.csv lists every claim I want resolved. Each row has a claim_id, the
meeting date, the quantifier the minutes used, and the sentence from the minutes. There are 183
rows across eight 2020 meetings. Treat it as the fixed list. Do not add rows and do not skip
rows.

The transcripts carry the original speaker labels, and the list at the top of each set of minutes
tells you who attended that meeting as a participant and who was there as staff. Here is every
file I am giving you, meeting by meeting.

The January 28 and 29 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-01-29.txt
/input_artifacts/minutes/fomc-minutes-2020-01-29.txt

The March 15 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-03-15.txt
/input_artifacts/minutes/fomc-minutes-2020-03-15.txt

The April 28 and 29 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-04-29.txt
/input_artifacts/minutes/fomc-minutes-2020-04-29.txt

The June 9 and 10 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-06-10.txt
/input_artifacts/minutes/fomc-minutes-2020-06-10.txt

The July 28 and 29 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-07-29.txt
/input_artifacts/minutes/fomc-minutes-2020-07-29.txt

The September 15 and 16 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-09-16.txt
/input_artifacts/minutes/fomc-minutes-2020-09-16.txt

The November 4 and 5 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-11-05.txt
/input_artifacts/minutes/fomc-minutes-2020-11-05.txt

The December 15 and 16 meeting:
/input_artifacts/transcripts/fomc-transcript-2020-12-16.txt
/input_artifacts/minutes/fomc-minutes-2020-12-16.txt

What I need back.

For every row in claims.csv, write one record into the directory /logs/agent/claim_records/ and
name the file after that row's claim_id, so the id 20200729-01 becomes a file called
20200729-01.json. Use the claim_id exactly as it appears in the file. Each record is a JSON
object with four
fields, named claim_id, meeting_date, roster and counterpoints. Put the claim_id in as it
appears in claims.csv and the meeting date in as it appears there too, in the year-month-day
form. The roster and counterpoints fields are both lists, and each entry in either list is an
object with two fields, speaker and quote.

The roster is the participants whose own remarks at that meeting express the view the claim
describes. For each one give me their surname as the transcript writes it, and one quotation
copied exactly from that participant's own remarks at that meeting. Put everyone on the roster
you can actually support. If the minutes say several and you can support six, give me six; if
you can only support two, give me two.

The counterpoints list is for participants at that same meeting whose remarks argue against the
claim, doubt it, or say the step it describes is unnecessary. Same shape as the roster, a
surname and an exact quotation. Most claims will have none, and an empty list is a real answer.
Do not invent disagreement to fill it. A participant can appear on both lists if they said both
things.

Only participants belong on either list. The staff brief the meeting and answer questions, and
their remarks are not participant views, so keep them out.

The quotations are the part I care most about, because they are what a referee will check. Each
one has to be a continuous run of words lifted from that participant's own remarks at that
meeting, and it has to come from the passage where they actually say it rather than from
somewhere else they happened to use similar words. Give me at least ten words, since a shorter
fragment will not stand on its own in a footnote, and keep it to roughly a sentence or two. Do
not stitch two passages together and do not tidy up the wording. The transcripts are hard
wrapped, so a quotation of any length will run across line breaks; that is fine and I only care
that the words themselves are unchanged.

Also write /logs/agent/attribution_matrix.csv, one row per claim and one column per participant
who appears anywhere in your rosters, marking which participants you placed on which claim. It
has to agree with the records, because I will be reading them side by side.

Output location - read before you start writing files.

Your shell's current working directory is /workspace. That directory is temporary scratch space
only. Clone repositories there, run builds there, and do any intermediate work you need there.
Nothing written under /workspace is preserved after this session ends.

Every deliverable I asked for must be written using its full absolute path starting with
/logs/agent/. Do not write deliverables to ./, ~/, /workspace/, or any path that is not
explicitly under /logs/agent/.

If a file is not physically present under /logs/agent/ when this session ends, it does not exist
for grading purposes. There is no partial-credit or /workspace exception. Before finishing, run
ls -la /logs/agent/ and confirm every requested deliverable is listed there with a non-zero
size.

One other practical thing.

If you run short of room, fewer records you are confident in are worth more to me than a full
set with guessed rosters. A wrong attribution in a published paper is worse than a gap in one,
and I would rather defend a short table than retract a long one.
