Hey, I'm putting together a lecture deck for an intro finance course and I could use a hand building it out. The textbook is `Principles of Finance` (sitting at `/input_artifacts/Principles_Finance.pdf`), and I want it summarize down into slides students can actually follow along with.

The book has about 630 pages: 20 numbered chapters, plus the usual front matter and back matter you can ignore. What I need is for someone to go through it and distill each chapter down to its essential talking points in slide form.

Here's the deck I'm picturing

A single PowerPoint that moves through the book in order, one chapter at a time, surfacing what actually matters in each chapter.

- Work through it sequentially, Chapter 1 to Chapter 20.
- Give each chapter no more than 5 slides. Treat that as a ceiling, not a quota - lean chapters can get away with fewer. What goes on those slides is the chapter's real meat: the central ideas, the definitions and formulas that matter, the models it introduces, and the conclusions it lands on.
- Write them like talking points, not paragraphs. Tight bullets a lecturer can speak to, anchored in the chapter's own specifics - the named models, the actual formulas, the precise terms - never the kind of generic line that would fit any chapter.
- Stick to the source. Every bullet has to trace back to that chapter of the book. No outside finance lore, no filling gaps with plausible-sounding extras - if the chapter doesn't say it, it stays off the slide.

Skip the front matter and appendices; the 20 numbered chapters are the whole job.

Give me an actual PowerPoint file (`.pptx`), saved at `/logs/agent/output.pptx`.

A few ground rules for the file:

- It's one deck, all 20 chapters, in chapter order.
- Open every chapter with a slide titled exactly `Chapter N: <chapter title>` (the book's real title for that chapter). I rely on those title slides to step through the deck chapter by chapter, so none can be missing.
- The chapter's key-point slides follow that title slide - and the title slide counts toward the 5-slide ceiling, so it's up to 5 slides per chapter all in.
- Stay faithful to the book the whole way through: real concepts, real terminology, nothing fabricated.

Conveniences in the environment (optional - use them or not, your choice)

- The book is pre-chopped by chapter at `/opt/book_chapters/chapter_NN.txt` (zero-padded - `/opt/book_chapters/chapter_07.txt` holds Chapter 7 and nothing else), so you can pull up a single chapter at a time instead of parsing the whole PDF. If `/opt/book_chapters/UNAVAILABLE` is present, read from the PDF instead. Either way the full PDF stays at `/input_artifacts/Principles_Finance.pdf`.
- A deck builder, `/opt/assemble_deck.py`, turns per-chapter slide files into the final deck. Drop each chapter's slides at `/logs/agent/chapter_NN_slides.json` (zero-padded) shaped like `{"chapter": N, "title": "<chapter title>", "slides": [{"title": "...", "bullets": ["...", "..."]}, ...]}` (up to 5 slides, first one titled `Chapter N: <title>`), then run `python3 /opt/assemble_deck.py /logs/agent/output.pptx /logs/agent` and it stitches them, in chapter order, into `/logs/agent/output.pptx`.

Neither shortcut is required. If you'd rather read straight from the PDF at `/input_artifacts/Principles_Finance.pdf` and write `/logs/agent/output.pptx` your own way, go for it - they only exist to save you time.

That's the whole ask.
