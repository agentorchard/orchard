# Psychology of Intelligence Analysis — audiobook source text

## What we are doing

The goal is an **audiobook** of Richards J. Heuer, Jr., *Psychology of
Intelligence Analysis*, made from the CIA's PDF of the book.

The Markdown in this directory is the narration script. It is not the end
product and it is not a reading copy — it exists to be spoken. Every question
about it resolves to two tests: **is this what the book actually says**, and
**does it work when read aloud**.

Claude's job is to produce that text from the PDF, and to prove it is right.

## Where things stand

| | |
| --- | --- |
| Extracted and verified | chapters 1 and 2 |
| Not yet extracted | chapters 3–14, and all front matter |
| Book structure | 4 parts, 14 chapters, 3 front-matter pieces (see below) |

The audiobook has no concept of parts — only a flat list of chapters. The
mapping from the book's parts and chapters onto that flat list is in
`audiobook-chapters.md`.

## Converting a chapter

```sh
python3 tools/heuer_extract.py N        # writes chapter-NN.md and its figures
python3 tools/test_heuer_extract.py     # snapshot + invariants
```

`tools/heuer_extract.py` is the only supported way to produce this text.

**Never hand-edit the Markdown.** It is regenerated from the PDF, so edits are
silently overwritten and the next person cannot tell which words are the book's
and which are ours. If the output is wrong, fix the extractor and re-run. That
is the whole point of having a script.

The extractor finds chapters by their `Chapter N` opener. The Author's Preface,
Foreword and Introduction have no such opener and cannot be extracted today;
adding them needs a small extension to the extractor, not a hand transcription.

## Division of labour: what is checked, and what is not

`tools/test_heuer_extract.py` enforces the mechanical properties of the output.
Read its docstring for the current list. **Do not restate those rules here** —
they live with the code so that they change together with it, and a second copy
in this file would go stale and start contradicting the test.

What that test cannot do is tell you whether the words are the book's words. It
compares the extractor against *its own previous output*, so a fault that was
present when a snapshot was approved stays approved forever, and a fault in a
chapter nobody has verified looks exactly like success. Everything below is in
that gap.

## Rules for the output that nothing enforces

These are properties of the text. No assertion inside the script establishes
them, because the script has no idea what the book says. They are true only when
someone has confirmed them against the book itself.

### Fidelity to the book

1. **Nothing missing, duplicated, or reordered.** Whole paragraphs can vanish
   at a page boundary or between a figure and the text around it, and the output
   still reads perfectly.
2. **Chapter boundaries are right.** The first and last paragraph of the file
   are the first and last paragraph of the chapter — not the tail of the
   previous chapter, not the head of the next.
3. **Proper nouns are spelled as the book spells them.** This PDF carries no
   Unicode mapping, so mis-read ligatures produce *plausible* wrong words, not
   obvious garbage. "Westerfeld" for Westerfield survived an entire hand review
   because it looks like a real surname. Check every name, journal title and
   publisher against the source.
4. **Hyphens mean what they meant on the page.** A hyphen at a line break joins
   a word; a hyphen between two numbers is a range. Getting this backwards turns
   "1973-1975" into "19731975", which a narrator will read as a single number.
5. **Paragraph breaks are the book's.** Breaks are inferred from indentation, so
   a page with an unusual margin can merge two paragraphs or split one.
6. **Footnote text is not in the body, and body text is not in the footnotes.**
   Both are inferred from type size.
7. **Block quotations are quotations.** They are set smaller than the body, which
   makes them easy to mistake for footnotes and swallow.
8. **The chapter title is the title.** Section headings set in display type
   elsewhere in the chapter must not be absorbed into it.
9. **Bullets are an inference, not a reading.** The bullet glyph comes from a
   font with no Unicode mapping. A list is recognised by position and rendered
   as a Markdown list. Confirm the list really is a list.
10. **A horizontal rule means the book's ornament break.** Same caveat: the
    ornament glyphs are undecodable and recognised by shape of use.
11. **Figures are in reading order and actually render.** Open every PNG and
    look at it. An image extracted with the wrong colour handling comes out
    inverted or blank, and no test will notice.

### Reading aloud

The text is going to be spoken, so faults that a reader's eye would skip past
become audible defects. These are decisions about the narration script, and they
are ours to make — the book cannot answer them.

12. **Nothing may be voiced that was never meant to be heard.** Footnote
    markers, figure paths and Markdown syntax are for the eye. Decide what the
    narration does with them; do not leave it to the TTS engine to guess.
13. **Anything visual needs a spoken equivalent or an explicit decision to drop
    it.** Chapter 2 turns on the reader looking at three triangles and at an
    ambiguous drawing of a woman. A listener cannot. Sentences like "when you
    looked at Figure 1 above, what did you see?" do not survive the move to
    audio untouched.
14. **Footnotes need a policy, applied consistently.** Read in place, read at the
    end of the chapter, or omitted — any of those can be right, but the same
    choice must hold across every chapter, and a citation-only note and a note
    carrying real argument are not the same thing. Chapter 2's note 27 explains
    the drawing; dropping it loses content.
15. **Abbreviations, acronyms and numbers get spoken forms where the written
    form misleads.** "Vol. 31, No. 1" and "p. 195" are not sentences.

**Open decisions.** Rules 12–14 are stated as requirements, not as answers. The
answers have not been chosen yet; choose them once, record them here, and then
they become checkable.

## Verification is mandatory, and adversarial

Any chapter that is not in `CHAPTERS` in `tools/test_heuer_extract.py` is
**unverified**, however clean it looks. A passing test run says nothing about it.

Before a new chapter is committed and added to `CHAPTERS`, review it like this:

1. **Start from the premise that it is wrong** and go looking for the evidence.
   A review that sets out to confirm the output finds nothing.
2. **Use an independent copy of the book and a different parser.** Checking our
   extractor against our extractor proves nothing. The Internet Archive holds a
   copy of the same edition whose text layer is intact —
   `archive.org/details/PsychologyOfIntelligenceAnalysis`, same 214-page
   pagination — and any third-party PDF library will do as the second parser.
   Both are for verification only. Neither may become a dependency of anything
   in `tools/` (see the supply-chain rule in the root `CLAUDE.md`).
3. **Diff body and notes separately.** Footnotes move to the end of the file, so
   a single whole-file diff drowns real differences in that one expected change.
4. **Check the order and presence of every block**, not just the word counts.
   Transposition and omission both leave the total plausible.
5. **Check every footnote's first and last words**, not just that the numbers
   are present. A truncated note still has a number.
6. **Look at every figure** as an image.
7. **Re-read the rules above one at a time** against the output. Each one exists
   because it was violated at least once.

Record what was checked in the commit message. "Verified" without saying against
what, and how, is worth nothing to the next person.

When the review passes, add the chapter to `CHAPTERS` and commit the snapshot.
From then on the test protects it.

## Structure of the book

Four parts, fourteen chapters, three front-matter pieces. PDF page numbers are
0-indexed, as the extractor counts them.

| Part | Chapters | PDF pages |
| --- | --- | --- |
| *(front matter)* | Author's Preface, Foreword, Introduction | 8–26 |
| I — Our Mental Machinery | 1–3 | 28–57 |
| II — Tools for Thinking | 4–8 | 58–137 |
| III — Cognitive Biases | 9–13 | 138–199 |
| IV — Conclusions | 14 | 200–211 |
