# Audiobook chapter mapping

The book is organised in two levels — four parts, each holding between one and
five chapters — plus three front-matter pieces. The audiobook has one level: a
flat, numbered list of chapters.

This is the proposed flattening. Nothing consumes it yet; it is a decision
record, so that the numbering is settled once rather than re-invented per
chapter.

## The shape of the problem

A part is not a chapter. Part III is 62 pages of material; Part IV is a single
chapter. Giving each part its own track produces four tracks of ten seconds
each, which is worse than useless on a phone — the listener taps past them and
loses their place.

So the parts are not tracks. They are carried in the **title of the first
chapter of each part**, where they are heard exactly once, at the moment they
become true, and where a listener scrubbing the chapter list can still see the
book's structure.

## Proposed mapping

17 tracks. Estimated runtimes at 150 words per minute, from the extracted text,
before any narration edits.

| # | Audiobook chapter title | Source | PDF pages | Words | Est. |
| ---: | --- | --- | --- | ---: | ---: |
| 01 | Author's Preface | front matter | 8–9 | 296 | 2 min |
| 02 | Foreword | front matter | 10–13 | 1,123 | 8 min |
| 03 | Introduction: Improving Intelligence Analysis at CIA | front matter | 14–26 | 4,215 | 28 min |
| 04 | Part One — Our Mental Machinery. Chapter 1: Thinking About Thinking | I / 1 | 28–33 | 2,241 | 15 min |
| 05 | Chapter 2: Perception — Why Can't We See What Is There To Be Seen? | I / 2 | 34–43 | 3,162 | 21 min |
| 06 | Chapter 3: Memory — How Do We Remember What We Know? | I / 3 | 44–57 | 5,189 | 35 min |
| 07 | Part Two — Tools for Thinking. Chapter 4: Strategies for Analytical Judgment | II / 4 | 58–77 | 6,914 | 46 min |
| 08 | Chapter 5: Do You Really Need More Information? | II / 5 | 78–91 | 4,286 | 29 min |
| 09 | Chapter 6: Keeping an Open Mind | II / 6 | 92–111 | 6,621 | 44 min |
| 10 | Chapter 7: Structuring Analytical Problems | II / 7 | 112–121 | 2,598 | 17 min |
| 11 | Chapter 8: Analysis of Competing Hypotheses | II / 8 | 122–137 | 5,200 | 35 min |
| 12 | Part Three — Cognitive Biases. Chapter 9: What Are Cognitive Biases? | III / 9 | 138–141 | 853 | 6 min |
| 13 | Chapter 10: Biases in Evaluation of Evidence | III / 10 | 142–153 | 4,168 | 28 min |
| 14 | Chapter 11: Biases in Perception of Cause and Effect | III / 11 | 154–173 | 7,647 | 51 min |
| 15 | Chapter 12: Biases in Estimating Probabilities | III / 12 | 174–187 | 4,962 | 33 min |
| 16 | Chapter 13: Hindsight Biases in Evaluation of Intelligence Reporting | III / 13 | 188–199 | 3,968 | 27 min |
| 17 | Part Four — Conclusions. Chapter 14: Improving Intelligence Analysis | IV / 14 | 200–211 | 4,099 | 27 min |

**Total: 67,542 words, roughly 7.5 hours.**

Chapter 4's full title in the book is "Strategies for Analytical Judgment:
Transcending the Limits of Incomplete Information". It is shortened above
because a chapter list is read at a glance; the full title still belongs in the
narration.

## Why this shape

- **Track numbers are sequential and never restart.** A listener who is 40%
  through has a number that means something. Restarting at 1 in each part would
  give four "Chapter 1"s.
- **The book's own chapter numbers survive** inside the titles, so a reference
  in the text to "Chapter 8" still finds its target. The two numbering schemes
  are visibly different — `04` versus "Chapter 1" — which is the point.
- **Front matter is included but comes first**, so it can be skipped as a block.
  The Introduction is substantial, not throat-clearing: it is 28 minutes and is
  the best argument in the book for reading the rest of it.
- **Nothing is merged.** Chapter 9 is only six minutes, and the temptation is to
  fold it into Chapter 10. Resist it: the text cross-references chapters by
  number, and a merged track breaks those references for a listener.

## Alternative, if part announcements are unwanted

Drop the part prefixes and let the four parts exist only in the book, not the
audiobook. Titles become plain — `04  Chapter 1: Thinking About Thinking`. This
is cleaner to look at and loses the only signal that the book changes register
three times. Recommended only if the narration announces the parts itself.

## Not yet decided

Whether each track opens with a spoken title, and whether the footnote policy
(see `CLAUDE.md` in this directory) changes the runtimes above. Citation-only
footnotes are a large share of Chapters 10–13 and would add noticeably to them
if read aloud.
