#!/usr/bin/env python3
"""Extract a chapter of Heuer's *Psychology of Intelligence Analysis* to Markdown.

The CIA's PDF has no ToUnicode maps, so generic extractors mis-read it: ligature
glyphs (fi, fl, ff, ffi and a Th ligature named T_h) collapse to a single letter,
producing "difcult", "fnding", "Tinking". Generic extractors also invent spaces
from kerning ("Jer vis", "psycholog y") and lose paragraph breaks.

This reader works from the page content streams directly, so it gets those from
the document itself rather than guessing:

  * ligatures  - resolved through each font's /Differences glyph names
  * word gaps  - the strings already carry their spaces; kerning is ignored
  * paragraphs - first-line indent, measured from the text matrix
  * footnotes  - set two points smaller than the body; markers smaller still
  * italics    - taken from the font name

Stdlib only, by CLAUDE.md's supply-chain rule: no third-party runtime deps.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import ssl
import struct
import sys
import urllib.request
import zlib
from pathlib import Path

SOURCE_URL = "https://www.cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf"
SOURCE_SHA256 = "bc703f2140e39e14e277c1277a84055a2529161f90db6633136f5457b6c60849"
CITATION = ("Richards J. Heuer, Jr., Psychology of Intelligence Analysis "
            "(Washington, DC: Center for the Study of Intelligence, Central "
            "Intelligence Agency, 1999). A work of the US Government: public domain.")


# --------------------------------------------------------------------------
# PDF object layer
# --------------------------------------------------------------------------
def _closer(s: bytes, op: bytes, cl: bytes) -> int:
    """Index of the delimiter closing the one that opens `s`."""
    depth = i = 0
    while i < len(s):
        if s[i:i + len(op)] == op:
            depth += 1
            i += len(op)
        elif s[i:i + len(cl)] == cl:
            depth -= 1
            if depth == 0:
                return i
            i += len(cl)
        else:
            i += 1
    return len(s) - 1


class Pdf:
    """Just enough PDF to reach page content streams and their resources."""

    def __init__(self, data: bytes):
        self.data = data
        self.obj: dict[int, bytes] = {}
        for m in re.finditer(rb'(?<![0-9])(\d+)\s+(\d+)\s+obj\b', data):
            self.obj[int(m.group(1))] = data[m.end():data.find(b'endobj', m.end())]
        for body in list(self.obj.values()):
            if b'/ObjStm' in body[:400]:
                self._expand_object_stream(body)
        self.pages = self._page_order()

    def stream(self, body: bytes) -> bytes | None:
        m = re.search(rb'stream(\r\n|\r|\n)', body)
        if not m:
            return None
        raw = body[m.end():body.rfind(b'endstream')]
        if b'/FlateDecode' in body[:m.start()]:
            try:
                raw = zlib.decompressobj().decompress(raw)
            except zlib.error:
                return None
        return raw

    def _expand_object_stream(self, body: bytes) -> None:
        data = self.stream(body)
        n = re.search(rb'/N\s+(\d+)', body)
        first = re.search(rb'/First\s+(\d+)', body)
        if not (data and n and first):
            return
        n, first = int(n.group(1)), int(first.group(1))
        nums = list(map(int, data[:first].split()))
        for i in range(n):
            num, off = nums[2 * i], nums[2 * i + 1]
            end = first + (nums[2 * i + 3] if i + 1 < n else len(data) - first)
            self.obj.setdefault(num, data[first + off:end])

    def deref(self, tok: bytes | None) -> bytes | None:
        if not tok:
            return tok
        m = re.match(rb'^\s*(\d+)\s+\d+\s+R\s*$', tok)
        return self.obj.get(int(m.group(1))) if m else tok

    @staticmethod
    def entry(body: bytes, key: str) -> bytes | None:
        """Raw value of /key: a name, number, reference, array or dictionary."""
        m = re.search(rb'/' + key.encode() + rb'(?![A-Za-z0-9])\s*', body)
        if not m:
            return None
        rest = body[m.end():]
        if rest[:1] == b'[':
            return rest[:_closer(rest, b'[', b']') + 1]
        if rest[:2] == b'<<':
            return rest[:_closer(rest, b'<<', b'>>') + 2]
        m2 = re.match(rb'(\d+\s+\d+\s+R|/[^\s/\[\]<>()]+|[-\d.]+)', rest)
        return m2.group(1) if m2 else None

    def _page_order(self) -> list[int]:
        root = next((num for num, body in self.obj.items()
                     if re.search(rb'/Type\s*/Pages\b', body) and b'/Parent' not in body), None)
        if root is None:
            raise SystemExit("no page tree found; is this a PDF?")
        order: list[int] = []

        def walk(num: int) -> None:
            kids = self.entry(self.obj[num], 'Kids')
            if kids is None:
                order.append(num)
                return
            for k in re.finditer(rb'(\d+)\s+\d+\s+R', kids):
                walk(int(k.group(1)))

        walk(root)
        return order

    def content(self, page: int) -> bytes:
        refs = self.entry(self.obj[self.pages[page]], 'Contents') or b''
        return b'\n'.join((self.stream(self.obj[int(m.group(1))]) or b'')
                          for m in re.finditer(rb'(\d+)\s+\d+\s+R', refs))

    def resources(self, page: int) -> bytes:
        res = self.entry(self.obj[self.pages[page]], 'Resources')
        return (res if res and res[:2] == b'<<' else self.deref(res)) or b''


# --------------------------------------------------------------------------
# Fonts and text runs
# --------------------------------------------------------------------------
GLYPH = {
    'T_h': 'Th', 'fi': 'fi', 'fl': 'fl', 'ff': 'ff', 'ffi': 'ffi', 'ffl': 'ffl',
    'space': ' ', 'quotesingle': "'", 'grave': '`',
    'emdash': '—', 'endash': '–', 'minus': '−', 'fraction': '⁄',
    'quotedblleft': '“', 'quotedblright': '”', 'quoteleft': '‘',
    'quoteright': '’', 'quotedblbase': '„', 'quotesinglbase': '‚',
    'guilsinglleft': '‹', 'guilsinglright': '›',
    'bullet': '•', 'ellipsis': '…', 'dagger': '†', 'daggerdbl': '‡',
    'perthousand': '‰', 'florin': 'ƒ', 'trademark': '™',
    'dotlessi': 'ı', 'Lslash': 'Ł', 'lslash': 'ł', 'OE': 'Œ',
    'oe': 'œ', 'Scaron': 'Š', 'scaron': 'š', 'Ydieresis': 'Ÿ',
    'Zcaron': 'Ž', 'zcaron': 'ž',
}
_ESCAPES = {b'n': '\n', b'r': '\r', b't': '\t', b'b': '\b', b'f': '\f',
            b'(': '(', b')': ')', b'\\': '\\'}


def _codes(raw: bytes) -> list[int]:
    """Byte codes of a PDF literal string, resolving backslash escapes."""
    out: list[int] = []
    i = 0
    while i < len(raw):
        if raw[i:i + 1] != b'\\':
            out.append(raw[i])
            i += 1
            continue
        nxt = raw[i + 1:i + 2]
        if nxt in _ESCAPES:
            out.append(ord(_ESCAPES[nxt]))
            i += 2
        elif nxt.isdigit():
            octal = re.match(rb'[0-7]{1,3}', raw[i + 1:]).group(0)
            out.append(int(octal, 8))
            i += 1 + len(octal)
        elif nxt in (b'\n', b'\r'):
            i += 2
        else:
            out.append(raw[i + 1])
            i += 2
    return out


class Font:
    def __init__(self, pdf: Pdf, body: bytes):
        self.name = (Pdf.entry(body, 'BaseFont') or b'/?').decode('latin-1').lstrip('/')
        low = self.name.lower()
        self.italic = 'italic' in low or low.endswith('it')
        self.composite = b'/Type0' in (Pdf.entry(body, 'Subtype') or b'')
        self.code_to_glyph: dict[int, str] = {}
        enc = Pdf.entry(body, 'Encoding')
        enc = enc if (enc and enc[:2] == b'<<') else pdf.deref(enc)
        if enc and b'/Differences' in enc:
            code = 0
            for number, name in re.findall(rb'(\d+)|/([^\s/\[\]]+)', Pdf.entry(enc, 'Differences')):
                if number:
                    code = int(number)
                else:
                    glyph = GLYPH.get(name.decode('latin-1'))
                    if glyph is not None:
                        self.code_to_glyph[code] = glyph
                    code += 1

    def decode(self, codes: list[int]) -> str:
        if self.composite:
            # Two-byte CIDs with no ToUnicode anywhere in this file: keep a
            # placeholder per glyph rather than silently dropping it.
            return ORNAMENT * (len(codes) // 2)
        out = []
        for c in codes:
            glyph = self.code_to_glyph.get(c)
            if glyph is None:
                glyph = bytes([c]).decode('cp1252', 'replace')
            out.append(glyph)
        return ''.join(out)


class Run:
    """A string drawn at one position, in one font."""
    __slots__ = ('x', 'y', 'size', 'italic', 'text')

    def __init__(self, x, y, size, italic, text):
        self.x, self.y, self.size, self.italic, self.text = x, y, size, italic, text

    def __repr__(self):
        return f'Run(x={self.x:.1f}, y={self.y:.1f}, {self.size:.0f}pt, {self.text!r})'


ORNAMENT = '￼'   # a glyph from a CID font this PDF gives no ToUnicode for

_STRING = rb'\((?:[^()\\]|\\.)*\)'
_HEX = rb'<[0-9A-Fa-f\s]*>'
# An array element may be a string containing brackets, so brackets alone
# cannot delimit the array.
_TOKEN = re.compile(rb'(<<.*?>>|\[(?:' + _STRING + rb'|' + _HEX + rb'|[^\[\]])*\]|'
                    + _STRING + rb'|' + _HEX + rb'|/[^\s/\[\]<>()]+|[-\d.]+|[A-Za-z\'"*]+)', re.S)


def page_runs(pdf: Pdf, page: int, stats: dict | None = None) -> list[Run]:
    res = pdf.resources(page)
    fonts: dict[str, Font] = {}
    fdict = Pdf.entry(res, 'Font')
    if fdict:
        fdict = fdict if fdict[:2] == b'<<' else pdf.deref(fdict)
        for m in re.finditer(rb'/(\w+)\s+(\d+)\s+\d+\s+R', fdict or b''):
            fonts[m.group(1).decode()] = Font(pdf, pdf.obj[int(m.group(2))])

    runs: list[Run] = []
    font: Font | None = None
    tm = [1.0, 0, 0, 1.0, 0.0, 0.0]
    line = tm[:]
    leading = 0.0
    args: list[bytes] = []

    def num(i: int) -> float:
        try:
            return float(args[i])
        except (ValueError, IndexError):
            return 0.0

    for m in _TOKEN.finditer(pdf.content(page)):
        tok = m.group(1)
        if re.match(rb'^[-\d./<(\[]', tok):
            args.append(tok)
            continue
        op = tok
        if op == b'Tf' and len(args) >= 2:
            font = fonts.get(args[-2].decode('latin-1').lstrip('/'))
        elif op == b'TL':
            leading = num(-1)
        elif op == b'Tm' and len(args) >= 6:
            tm = [num(-6), num(-5), num(-4), num(-3), num(-2), num(-1)]
            line = tm[:]
        elif op in (b'Td', b'TD') and len(args) >= 2:
            if op == b'TD':
                leading = -num(-1)
            dx, dy = num(-2), num(-1)
            line = line[:4] + [line[4] + dx * line[0] + dy * line[2],
                               line[5] + dx * line[1] + dy * line[3]]
            tm = line[:]
        elif op == b'T*':
            line = line[:4] + [line[4] - leading * line[2], line[5] - leading * line[3]]
            tm = line[:]
        elif op in (b'Tj', b'TJ', b"'", b'"'):
            if op in (b"'", b'"'):
                line = line[:4] + [line[4] - leading * line[2], line[5] - leading * line[3]]
                tm = line[:]
            arg = args[-1] if args else b''
            chunks = (re.findall(_STRING + rb'|' + _HEX, arg, re.S)
                      if op == b'TJ' else [arg])
            text = ''
            if font:
                for c in chunks:
                    inner = c[1:-1]
                    codes = (list(bytes.fromhex(re.sub(rb'\s', b'', inner).decode('ascii')))
                             if c[:1] == b'<' else _codes(inner))
                    text += font.decode(codes)
                    if stats is not None:      # bytes consumed, for the coverage check
                        stats['bytes'] = stats.get('bytes', 0) + len(codes)
            if text.strip():
                runs.append(Run(tm[4], tm[5], abs(tm[3]) or abs(tm[0]),
                                bool(font and font.italic), text))
        if op.isalpha() or op in (b"'", b'"'):
            args = []
    return runs


def literal_chars(content: bytes) -> int:
    """Characters inside string literals, counted without the tokenizer.

    Compared against what the tokenizer actually decoded, this catches a
    malformed operand silently swallowing part of a page.
    """
    total = i = depth = 0
    while i < len(content):
        c = content[i:i + 1]
        if depth:
            if c == b'\\':
                octal = re.match(rb'[0-7]{1,3}', content[i + 1:])
                total += 1
                i += 1 + (len(octal.group(0)) if octal else 1)
                continue
            if c == b'(':
                depth += 1
            elif c == b')':
                depth -= 1
                i += 1
                continue
            total += 1
            i += 1
            continue
        if c == b'(':
            depth = 1
        elif c == b'<' and content[i + 1:i + 2] != b'<':
            end = content.find(b'>', i)
            digits = re.sub(rb'\s', b'', content[i + 1:end]) if end > 0 else b'x'
            if end > 0 and re.fullmatch(rb'[0-9A-Fa-f]*', digits):
                total += len(digits) // 2
                i = end + 1
                continue
        i += 1
    return total


def page_figures(pdf: Pdf, page: int) -> list[dict]:
    """Image XObjects drawn on the page, with the box they are painted into."""
    res = pdf.resources(page)
    xobjects = Pdf.entry(res, 'XObject')
    if not xobjects:
        return []
    by_name = {m.group(1).decode(): int(m.group(2))
               for m in re.finditer(rb'/(\w+)\s+(\d+)\s+\d+\s+R', xobjects)}
    out, seen = [], set()
    pattern = re.compile(rb'([-\d.]+)\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)'
                         rb'\s+cm\s*/(\w+)\s+Do')
    for m in pattern.finditer(pdf.content(page)):
        name = m.group(5).decode()
        num = by_name.get(name)
        if num is None or num in seen:
            continue
        body = pdf.obj[num]
        if not re.search(rb'/Subtype\s*/Image', body):
            continue
        seen.add(num)
        out.append({'obj': num, 'width': float(m.group(1)), 'height': float(m.group(2)),
                    'x': float(m.group(3)), 'y': float(m.group(4))})
    return out


def figure_png(pdf: Pdf, obj: int) -> bytes | None:
    """Re-wrap an 8-bit greyscale/indexed image XObject as a PNG."""
    body = pdf.obj[obj]
    if b'/DCTDecode' in body:
        return None                          # already a JPEG; caller writes it verbatim
    samples = pdf.stream(body)
    space = Pdf.entry(body, 'ColorSpace')
    space = pdf.deref(space) if space and space[:1] != b'/' else space
    inked = bool(space and (b'/DeviceN' in space or b'/Separation' in space))
    w = Pdf.entry(body, 'Width')
    h = Pdf.entry(body, 'Height')
    bpc = Pdf.entry(body, 'BitsPerComponent')
    if not (samples and w and h) or (bpc and int(bpc) != 8):
        return None
    w, h = int(w), int(h)
    channels = len(samples) // (w * h) if w * h else 0
    if channels not in (1, 3):
        return None
    if inked:                       # 0 means no ink, i.e. white
        samples = bytes(255 - v for v in samples)
    colour = {1: 0, 3: 2}[channels]
    rows = b''.join(b'\x00' + samples[r * w * channels:(r + 1) * w * channels] for r in range(h))

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack('>I', len(payload)) + tag + payload
                + struct.pack('>I', zlib.crc32(tag + payload) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, colour, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9))
            + chunk(b'IEND', b''))


# --------------------------------------------------------------------------
# Lines and structure
# --------------------------------------------------------------------------
class Line:
    __slots__ = ('y', 'x', 'size', 'runs')

    def __init__(self, y, x, size, runs):
        self.y, self.x, self.size, self.runs = y, x, size, runs

    @property
    def text(self) -> str:
        return ''.join(r.text for r in self.runs)


def page_lines(pdf: Pdf, page: int, marker_ratio: float = 0.75,
               stats: dict | None = None) -> list[Line]:
    """Runs grouped into lines, top-down. Superscripts join the line they sit on."""
    runs = page_runs(pdf, page, stats)
    if not runs:
        return []
    body_size = max(r.size for r in runs)
    lines: list[Line] = []
    for run in runs:
        host = next((ln for ln in lines
                     if abs(ln.y - run.y) <= max(1.5, 0.35 * ln.size)
                     or (run.size < marker_ratio * ln.size and abs(ln.y - run.y) <= 0.5 * ln.size)),
                    None)
        if host is None:
            lines.append(Line(run.y, run.x, run.size, [run]))
        else:
            host.runs.append(run)
            host.x = min(host.x, run.x)
            host.size = max(host.size, run.size)
    del body_size
    lines.sort(key=lambda ln: -ln.y)
    return lines


def _mode(values: list[float]) -> float:
    return max(set(values), key=values.count) if values else 0.0


class Segment:
    __slots__ = ('text', 'italic')

    def __init__(self, text, italic):
        self.text, self.italic = text, italic


def _join(segments: list[Segment], line_segments: list[Segment]) -> None:
    """Append a line to a paragraph, healing end-of-line hyphenation.

    The hyphen is often a run of its own, so the decision is made on the
    paragraph text so far, not on the last segment alone.
    """
    if segments:
        whole = ''.join(seg.text for seg in segments).rstrip()
        head = line_segments[0].text.lstrip() if line_segments else ''
        for seg in reversed(segments):
            if seg.text.strip():
                seg.text = seg.text.rstrip()
                break
        # A hyphen between two digits is part of a range ("1973-1975"), not a
        # word broken across lines.
        if whole.endswith('-'):
            if not (whole[-2:-1].isdigit() and head[:1].isdigit()):
                for seg in reversed(segments):       # word broken across lines
                    if seg.text.endswith('-'):
                        seg.text = seg.text[:-1]
                        break
        else:
            for seg in reversed(segments):
                if seg.text:
                    seg.text += ' '
                    break
    segments.extend(line_segments)


def _render(segments: list[Segment]) -> str:
    # Punctuation set in a neighbouring face (an opening quote, a hyphen) must
    # not open or close an emphasis span of its own.
    for i, seg in enumerate(segments):
        if seg.italic and not any(c.isalnum() for c in seg.text):
            seg.italic = segments[i - 1].italic if i else False
    merged: list[Segment] = []
    for seg in segments:
        if merged and merged[-1].italic == seg.italic:
            merged[-1].text += seg.text
        elif seg.text:
            merged.append(Segment(seg.text, seg.italic))
    out = []
    for seg in merged:
        text = re.sub(r'\s+', ' ', seg.text)
        if not seg.italic or not text.strip():
            out.append(text)
            continue
        lead = ' ' if text[:1] == ' ' else ''
        trail = ' ' if text[-1:] == ' ' else ''
        out.append(f'{lead}*{text.strip()}*{trail}')
    return re.sub(r' {2,}', ' ', ''.join(out)).strip()


def chapter_starts(pdf: Pdf) -> dict[int, int]:
    """Chapter number -> page index, from the chapter openers' display type."""
    starts: dict[int, int] = {}
    for page in range(len(pdf.pages)):
        for line in page_lines(pdf, page)[:4]:
            m = re.match(r'^Chapter\s+(\d+)\s*$', line.text.strip())
            if m and line.size >= 14:
                starts.setdefault(int(m.group(1)), page)
    return starts


def extract_chapter(pdf: Pdf, number: int, figure_dir: Path | None = None,
                    figure_prefix: str = '') -> tuple[str, list[str]]:
    """Markdown for one chapter, plus anything the reader could not account for."""
    starts = chapter_starts(pdf)
    if number not in starts:
        raise SystemExit(f"chapter {number} not found; this PDF has {sorted(starts)}")
    first = starts[number]
    later = [p for n, p in starts.items() if p > first]
    last = (min(later) - 1) if later else len(pdf.pages) - 1

    warnings: list[str] = []
    notes: list[tuple[int, list[Segment]]] = []
    blocks: list[tuple[str, object]] = []
    part: str | None = None
    title_parts: list[str] = []
    current: list[Segment] = []
    kind = 'p'

    all_sizes = [round(ln.size, 1)
                 for p in range(first, last + 1) for ln in page_lines(pdf, p)]
    body_size = _mode(all_sizes)
    note_size = min(all_sizes)                 # footnotes are the smallest type

    def flush() -> None:
        nonlocal current
        if current:
            blocks.append((kind, _render(current)))
            current = []

    for page in range(first, last + 1):
        stats: dict = {}
        lines = page_lines(pdf, page, stats=stats)
        expected = literal_chars(pdf.content(page))
        if stats.get('bytes', 0) < expected:
            warnings.append(f'page {page + 1}: decoded {stats.get("bytes", 0)} of '
                            f'{expected} string bytes - text may be missing')
        folio = [ln for ln in lines
                 if abs(ln.size - body_size) < 0.1 and ln.text.strip().isdigit()
                 and ln.y < 100]
        # Every page sets its own margin: chapter openers are inset further than
        # the rest, so a first-line indent only means anything on its own page.
        left = min((ln.x for ln in lines
                    if abs(ln.size - body_size) < 0.1 and ln not in folio), default=0.0)
        quote_left = min((ln.x for ln in lines
                          if note_size + 0.1 < ln.size < body_size - 0.1), default=0.0)
        figures = sorted(page_figures(pdf, page), key=lambda f: -f['y'])
        in_notes = in_list = False

        for line in lines:
            text = line.text
            if not text.strip() or line in folio:
                continue
            while figures and line.y < figures[0]['y']:
                flush()
                kind = 'p'
                blocks.append(('figure', figures.pop(0)))

            if line.size > body_size + 0.1:                       # display type
                stripped = text.strip()
                if stripped.startswith('PART'):
                    part = stripped
                elif re.match(r'^Chapter\s+\d+\s*$', stripped):
                    pass
                elif page == first:
                    title_parts.append(stripped)                  # chapter title
                else:
                    flush()
                    blocks.append(('h2', stripped))               # section heading
                continue

            if line.size <= note_size + 0.1:                      # footnote text
                in_notes = True
                opener = re.match(r'^(\d+)\.$', line.runs[0].text.strip()) or \
                    re.match(r'^(\d+)\.\s', text.strip())
                if opener and (not notes or int(opener.group(1)) > notes[-1][0]):
                    skip = len(text) - len(text.lstrip()) + len(opener.group(0))
                    notes.append((int(opener.group(1)), _segments(line, skip=skip)))
                elif notes:
                    _join(notes[-1][1], _segments(line))
                else:
                    warnings.append(f'page {page + 1}: footnote text before any marker')
                continue
            if in_notes:
                continue                     # body never resumes below the notes

            if set(text.strip()) == {ORNAMENT}:                   # ornament rule
                flush()
                kind = 'p'
                blocks.append(('rule', None))
                in_list = False
                continue

            if line.size < body_size - 0.1:                       # block quotation
                if kind != 'quote' or line.x > quote_left + 10:
                    flush()
                kind = 'quote'
                in_list = False
                _join(current, _segments(line, body_size=line.size, marker=True))
                continue

            if kind == 'quote':
                flush()
                kind = 'p'

            bullet = text.lstrip().startswith(ORNAMENT)
            if bullet:
                flush()
                kind = 'li'
                in_list = True
                segs = _segments(line, body_size=line.size, marker=True)
                segs[0].text = segs[0].text.lstrip(ORNAMENT + ' \t')
                current.extend(s for s in segs if s.text)
                continue
            indented = line.x > left + 10
            if in_list and indented:
                _join(current, _segments(line, body_size=line.size, marker=True))
                continue
            in_list = False
            if kind == 'li':
                flush()
                kind = 'p'
            if ORNAMENT in text:
                warnings.append(f'page {page + 1}: undecodable glyph kept as U+FFFC')
            if indented and current:                              # first-line indent
                flush()
            _join(current, _segments(line, body_size=line.size, marker=True))
    flush()

    if not blocks:
        warnings.append('no body text found')
    title = ' '.join(title_parts).strip()
    md = _markdown(number, title, part, blocks, notes, figure_dir, figure_prefix,
                   pdf, warnings)
    return md, warnings


def _segments(line: Line, skip: int = 0, body_size: float | None = None,
              marker: bool = False) -> list[Segment]:
    segs: list[Segment] = []
    for run in line.runs:
        text = run.text
        if marker and body_size and run.size < body_size - 0.5:
            digits = text.strip()
            if digits.isdigit():                       # superscript note marker
                lead = text[:len(text) - len(text.lstrip())]
                trail = text[len(text.rstrip()):]
                segs.append(Segment(f'{lead}[^{digits}]{trail}', False))
                continue
        segs.append(Segment(text, run.italic))
    if skip:
        while skip > 0 and segs:
            if len(segs[0].text) <= skip:
                skip -= len(segs[0].text)
                segs.pop(0)
            else:
                segs[0].text = segs[0].text[skip:]
                skip = 0
    return [s for s in segs if s.text]


def _markdown(number, title, part, blocks, notes, figure_dir, figure_prefix,
              pdf, warnings) -> str:
    out = [f'# Chapter {number}: {title}' if title else f'# Chapter {number}']
    if part:
        out.append('*' + re.sub(r'\s*\u2014\s*', ' \u2014 ', part.title()) + '*')
    out.append(f'*{CITATION} Extracted from <{SOURCE_URL}> by `tools/heuer_extract.py`.*')
    for kind, value in blocks:
        if kind == 'rule':
            out.append('---')
        elif kind == 'figure':
            name = f'{figure_prefix}figure-{value["obj"]}.png'
            if figure_dir is None:
                out.append(f'<!-- figure: image object {value["obj"]} -->')
                continue
            png = figure_png(pdf, value['obj'])
            if png is None:
                warnings.append(f'image object {value["obj"]} is not 8-bit; not written')
                out.append(f'<!-- figure: image object {value["obj"]} not converted -->')
                continue
            figure_dir.mkdir(parents=True, exist_ok=True)
            (figure_dir / name).write_bytes(png)
            out.append(f'![Figure from the original]({figure_dir.name}/{name})')
        elif kind == 'h2':
            out.append(f'## {value}')
        elif kind == 'quote':
            out.append('> ' + str(value).replace('\n', '\n> '))
        elif kind == 'li':
            out.append(f'- {value}')
        else:
            out.append(value)
    if notes:
        out.append('---')
        out.append('## Notes')
        out.extend(f'[^{num}]: {_render(segs)}' for num, segs in sorted(notes))
    else:
        warnings.append('no footnotes found')
    return '\n\n'.join(out).rstrip() + '\n'


# --------------------------------------------------------------------------
# Source file
# --------------------------------------------------------------------------
def load_pdf(path: Path | None, url: str, expect_sha: str | None, allow_download: bool) -> bytes:
    if path and path.exists():
        data = path.read_bytes()
    elif not allow_download:
        raise SystemExit(f"{path} is missing and downloads are disabled")
    else:
        ctx = ssl.create_default_context()
        bundle = os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE')
        if bundle and Path(bundle).exists():
            ctx.load_verify_locations(bundle)
        with urllib.request.urlopen(url, context=ctx, timeout=120) as resp:
            data = resp.read()
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if expect_sha and digest != expect_sha:
        raise SystemExit(f"source PDF digest mismatch\n  expected {expect_sha}\n  got      {digest}")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('chapters', nargs='*', type=int, help='chapter numbers (default: 1)')
    ap.add_argument('--pdf', type=Path, default=Path('.cache/psychology-of-intelligence-analysis.pdf'))
    ap.add_argument('--out', type=Path, default=Path('docs/psychology-of-intelligence-analysis'))
    ap.add_argument('--no-download', action='store_true')
    ap.add_argument('--print-sha', action='store_true', help='print the source digest and exit')
    ap.add_argument('--stdout', action='store_true')
    args = ap.parse_args(argv)

    data = load_pdf(args.pdf, SOURCE_URL, None if args.print_sha else SOURCE_SHA256,
                    not args.no_download)
    if args.print_sha:
        print(hashlib.sha256(data).hexdigest())
        return 0

    pdf = Pdf(data)
    status = 0
    for number in (args.chapters or [1]):
        prefix = f'ch{number:02d}-'
        md, warnings = extract_chapter(pdf, number, None if args.stdout else args.out / 'figures', prefix)
        for w in warnings:
            print(f'warning: chapter {number}: {w}', file=sys.stderr)
            status = 1
        if args.stdout:
            print(md)
        else:
            args.out.mkdir(parents=True, exist_ok=True)
            target = args.out / f'chapter-{number:02d}.md'
            target.write_text(md, encoding='utf-8')
            print(f'wrote {target} ({len(md.split())} words)')
    return status


if __name__ == '__main__':
    raise SystemExit(main())
