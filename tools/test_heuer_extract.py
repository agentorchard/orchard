#!/usr/bin/env python3
"""Regression test for tools/heuer_extract.py.

Two layers, both stdlib only:

  Snapshot  - the committed Markdown under docs/ is the expected output. Any
              difference fails and is printed as a diff. A change that is an
              improvement is approved by re-running with --update and reviewing
              the diff in the commit.
  Invariant - checks that hold for any chapter, so a fix aimed at one chapter
              cannot quietly break another: full byte coverage of every page,
              footnote markers and definitions matching, no undecoded glyphs,
              and every referenced figure present on disk.

    python3 tools/test_heuer_extract.py            # check
    python3 tools/test_heuer_extract.py --update   # approve a deliberate change
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import heuer_extract as he                                       # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs' / 'psychology-of-intelligence-analysis'
CACHE = ROOT / '.cache' / 'psychology-of-intelligence-analysis.pdf'
CHAPTERS = (1, 2)


def invariants(chapter: int, md: str, warnings: list[str]) -> list[str]:
    """Properties every chapter must satisfy, whatever the text says."""
    failures = [f'extractor warning: {w}' for w in warnings]

    if he.ORNAMENT in md:
        failures.append('output contains an undecoded glyph (U+FFFC)')

    body, _, notes_block = md.partition('\n## Notes\n')
    used = [int(n) for n in re.findall(r'\[\^(\d+)\]', body)]
    defined = [int(n) for n in re.findall(r'^\[\^(\d+)\]:', notes_block, re.M)]
    if sorted(set(used)) != sorted(used):
        failures.append(f'footnote marker used twice in the body: {used}')
    if sorted(used) != sorted(defined):
        failures.append(f'markers {sorted(used)} do not match definitions {sorted(defined)}')
    if defined and defined != sorted(defined):
        failures.append('footnote definitions are out of order')
    if defined and defined != list(range(defined[0], defined[0] + len(defined))):
        failures.append(f'footnote numbers are not contiguous: {defined}')

    for note in re.findall(r'^\[\^\d+\]: *(.*)$', notes_block, re.M):
        if not note.strip():
            failures.append('a footnote is empty')

    words = len(body.split())
    if words < 1000:
        failures.append(f'body is only {words} words; the chapter is probably truncated')

    for target in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md):
        if not (DOCS / target).exists():
            failures.append(f'figure referenced but not on disk: {target}')

    if not md.startswith(f'# Chapter {chapter}:'):
        failures.append(f'heading is not "# Chapter {chapter}: ..."')

    unbalanced = [line for line in body.splitlines() if line.count('*') % 2]
    if unbalanced:
        failures.append(f'unbalanced emphasis on {len(unbalanced)} line(s), '
                        f'e.g. {unbalanced[0][:60]!r}')
    return failures


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--update', action='store_true',
                    help='rewrite the committed Markdown and figures from the PDF')
    ap.add_argument('--no-download', action='store_true')
    args = ap.parse_args(argv)

    data = he.load_pdf(CACHE, he.SOURCE_URL, he.SOURCE_SHA256, not args.no_download)
    print(f'source PDF: {len(data)} bytes, sha256 matches the pinned digest')
    pdf = he.Pdf(data)

    failures: list[str] = []
    for chapter in CHAPTERS:
        target = DOCS / f'chapter-{chapter:02d}.md'
        figures = DOCS / 'figures'
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(figures.glob(f'ch{chapter:02d}-*'))}
        md, warnings = he.extract_chapter(pdf, chapter, figures, f'ch{chapter:02d}-')
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(figures.glob(f'ch{chapter:02d}-*'))}

        problems = invariants(chapter, md, warnings)
        for problem in problems:
            failures.append(f'chapter {chapter}: {problem}')

        if args.update:
            target.write_text(md, encoding='utf-8')
            print(f'chapter {chapter}: snapshot updated ({len(md.split())} words)')
            continue

        expected = target.read_text(encoding='utf-8') if target.exists() else ''
        if md != expected:
            failures.append(f'chapter {chapter}: output differs from {target.relative_to(ROOT)}')
            diff = difflib.unified_diff(expected.splitlines(), md.splitlines(),
                                        fromfile=f'{target.name} (committed)',
                                        tofile=f'{target.name} (extractor)', lineterm='', n=1)
            print('\n'.join(list(diff)[:80]))
        if before and before != after:
            changed = [n for n in after if before.get(n) != after[n]]
            failures.append(f'chapter {chapter}: figure bytes changed: {changed}')
        note_count = len(re.findall(r'^\[\^', md, re.M))
        if not problems and md == expected:
            print(f'chapter {chapter}: matches snapshot '
                  f'({len(md.split())} words, {note_count} notes)')

    if failures:
        print('\nFAILED')
        for failure in failures:
            print(f'  - {failure}')
        print('\nIf a difference is an improvement, review the diff and approve it with:'
              '\n    python3 tools/test_heuer_extract.py --update')
        return 1
    print('\nOK' if not args.update else '\nsnapshots written')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
