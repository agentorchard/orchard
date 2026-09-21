# Psychology of Intelligence Analysis

Markdown extracted from Richards J. Heuer, Jr., *Psychology of Intelligence
Analysis* (Washington, DC: Center for the Study of Intelligence, Central
Intelligence Agency, 1999).

Source PDF: <https://www.cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf>
(sha256 `bc703f2140e39e14e277c1277a84055a2529161f90db6633136f5457b6c60849`, pinned
in `tools/heuer_extract.py`).

## Status

| File | Chapter | Verified against an independent copy |
| --- | --- | --- |
| `chapter-01.md` | 1 — Thinking About Thinking | yes, word for word |
| `chapter-02.md` | 2 — Perception: Why Can't We See What Is There To Be Seen? | yes, every paragraph and footnote |

Later chapters are not extracted yet. `python3 tools/heuer_extract.py 3` will
produce one; add it to `CHAPTERS` in `tools/test_heuer_extract.py` to hold it
under regression test, and verify it before committing.

## Licence

A work of the US Government, prepared by officers and employees as part of their
official duties, and therefore in the public domain in the United States. It is
not covered by this repository's Apache-2.0 licence, which applies to the code
under `tools/`, nor by CC0, which applies to registry data. Reproduced here with
attribution to the author and the Center for the Study of Intelligence.

## Regenerating

```sh
python3 tools/heuer_extract.py 1 2      # rewrite the Markdown and figures
python3 tools/test_heuer_extract.py     # check nothing changed unexpectedly
```

The extractor is deterministic: the same PDF always yields the same Markdown, so
any difference is a real change in the extractor and is reviewed as a diff.

## What the Markdown preserves

Paragraph breaks, section headings, block quotations, bullet lists, italics
(including book and journal titles in the footnotes), footnotes as Markdown
footnotes, figures as PNGs under `figures/`, and ligatures the PDF's own text
layer gets wrong.

## What it does not preserve

Page breaks and printed page numbers are dropped; footnotes move from the foot
of each page to a `## Notes` section at the end. The row of ornaments the book
uses as a section break becomes a horizontal rule. Bullet glyphs come from a
font the PDF gives no Unicode mapping for, so they are recognised by position
and rendered as a Markdown list.
