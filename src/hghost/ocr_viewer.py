"""Static side-by-side viewer for PaddleOCR-VL results: page image with block boxes, text beside it.

Reads the quarantined raw OCR outputs (``artifacts/paddle-ocr/raw``), renders the requested pages of the
source PDFs with Poppler's ``pdftoppm`` (read-only; the source trees are never modified), and writes one
HTML file per run under the output directory. Hovering a block highlights it on the page and in the text
column; layout labels are shown; nothing is admitted or rejected here, this is for looking.
"""

from __future__ import annotations

import argparse
import gzip
import html
import json
import subprocess
import webbrowser
from pathlib import Path

from .build_dataset import read_record as load_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render an HTML review page for OCR'd documents."
    )
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="name=path source root (repeatable)",
    )
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument(
        "--raw", type=Path, required=True, help="raw OCR output directory"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=6, help="documents to include")
    parser.add_argument("--pages", type=int, default=2, help="pages per document")
    parser.add_argument("--dpi", type=int, default=70)
    parser.add_argument(
        "--newest", action="store_true", help="pick the most recently written results"
    )
    parser.add_argument(
        "--open", action="store_true", help="open the result in the default browser"
    )
    return parser


def parse_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        name, _, path = value.partition("=")
        roots[name] = Path(path).expanduser().resolve()
    return roots


def render_page(pdf: Path, page_index: int, dpi: int, target: Path) -> Path | None:
    """Render one 0-based page to PNG via pdftoppm; returns the file or None on failure."""

    target.parent.mkdir(parents=True, exist_ok=True)
    prefix = target.with_suffix("")
    page = page_index + 1
    result = subprocess.run(
        [
            "pdftoppm",
            "-f",
            str(page),
            "-l",
            str(page),
            "-r",
            str(dpi),
            "-png",
            str(pdf),
            str(prefix),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    candidates = sorted(prefix.parent.glob(prefix.name + "*.png"))
    if not candidates:
        return None
    candidates[0].rename(target)
    return target


def block_html(
    doc_key: str,
    page_index: int,
    index: int,
    block: dict,
    scale_x: float,
    scale_y: float,
) -> tuple[str, str]:
    x0, y0, x1, y1 = block.get("bbox") or (0, 0, 0, 0)
    ident = f"{doc_key}-p{page_index}-b{index}"
    label = html.escape(str(block.get("label", "")))
    content = html.escape(str(block.get("content", "")))
    box = (
        f'<div class="box" data-block="{ident}" title="{label}" style="left:{x0 * scale_x:.1f}px;'
        f'top:{y0 * scale_y:.1f}px;width:{(x1 - x0) * scale_x:.1f}px;height:{(y1 - y0) * scale_y:.1f}px"></div>'
    )
    text = f'<div class="blk" data-block="{ident}"><span class="lbl">{label}</span>{content}</div>'
    return box, text


def main() -> None:
    args = build_parser().parse_args()
    roots = parse_roots(args.root)
    output: Path = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(
        args.raw.rglob("*.json.gz"),
        key=lambda p: p.stat().st_mtime,
        reverse=args.newest,
    )
    if not args.newest:
        raw_files = sorted(raw_files, key=lambda p: -p.stat().st_size)
    docs = []
    for raw_path in raw_files:
        with gzip.open(raw_path, "rt", encoding="utf-8") as handle:
            raw = json.load(handle)
        if raw.get("pages"):
            docs.append((raw_path, raw))
        if len(docs) >= args.limit:
            break

    record_index: dict[str, dict] = {}
    for path in args.records.rglob("*.json.gz"):
        record = load_record(path)
        record_index[record["document_id"]] = record

    sections = []
    for raw_path, raw in docs:
        doc_id = raw["document_id"]
        record = record_index.get(doc_id, {})
        source = raw["source"]
        pdf = roots[source] / raw["relative_path"]
        title = html.escape(f"{source}/{raw['relative_path']}")
        meta = html.escape(
            f"status {record.get('status', '?')} · {record.get('pages', '?')} pages · "
            f"{record.get('tokens', '?')} tokens · alpha {float(record.get('alpha_ratio') or 0):.2f} · "
            f"engine {raw.get('engine')} {raw.get('engine_version')}"
        )
        pages_html = []
        for page in raw["pages"][: args.pages]:
            page_index = int(page["page_index"])
            png = output / "pages" / f"{doc_id}-p{page_index}.png"
            rendered = render_page(pdf, page_index, args.dpi, png)
            if rendered is None:
                pages_html.append(
                    f"<p>page {page_index + 1}: could not render {title}</p>"
                )
                continue
            # pdftoppm output size is unknown until rendered; read it from the PNG header.
            with rendered.open("rb") as handle:
                header = handle.read(24)
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            scale_x = width / max(1, int(page.get("width") or width))
            scale_y = height / max(1, int(page.get("height") or height))
            boxes, texts = [], []
            for index, block in enumerate(page.get("blocks") or []):
                box, text = block_html(
                    doc_id, page_index, index, block, scale_x, scale_y
                )
                boxes.append(box)
                texts.append(text)
            pages_html.append(
                f'<div class="page"><div class="img" style="width:{width}px;height:{height}px">'
                f'<img src="pages/{png.name}" width="{width}" height="{height}">{"".join(boxes)}</div>'
                f'<div class="txt">{"".join(texts) or "<em>no blocks</em>"}</div></div>'
            )
        sections.append(
            f"<section><h2>{title}</h2><p class=meta>{meta}</p>{''.join(pages_html)}</section>"
        )

    page_html = f"""<!doctype html><meta charset="utf-8"><title>h ghost OCR viewer</title>
<style>
body{{font:14px/1.4 -apple-system,system-ui,sans-serif;margin:0;padding:16px;background:#111;color:#ddd}}
h1{{font-weight:500}} h2{{font-size:15px;margin:32px 0 4px}} .meta{{color:#888;margin:0 0 8px}}
.page{{display:flex;gap:16px;margin:12px 0;align-items:flex-start}}
.img{{position:relative;flex:none;background:#fff}} .img img{{display:block}}
.box{{position:absolute;border:1px solid rgba(255,80,80,.7);box-sizing:border-box}}
.box:hover,.box.hot{{background:rgba(255,80,80,.25);border-color:#ff5050}}
.txt{{flex:1;min-width:320px;max-height:{int(1600 * args.dpi / 100)}px;overflow:auto;background:#181818;padding:8px;border-radius:6px}}
.blk{{padding:4px 6px;border-left:3px solid #333;margin:2px 0;white-space:pre-wrap}}
.blk:hover,.blk.hot{{background:#2a2222;border-left-color:#ff5050}}
.lbl{{display:inline-block;font-size:11px;color:#999;margin-right:6px;font-family:ui-monospace,monospace}}
</style>
<h1>h ghost · PaddleOCR-VL results (quarantined, unreviewed)</h1>
<p class=meta>{len(docs)} documents · first {args.pages} page(s) each · boxes are layout blocks; hover to pair image and text</p>
{"".join(sections)}
<script>
for (const el of document.querySelectorAll('[data-block]')) {{
  const key = el.dataset.block;
  el.addEventListener('mouseenter', () => document.querySelectorAll('[data-block="'+key+'"]').forEach(e => e.classList.add('hot')));
  el.addEventListener('mouseleave', () => document.querySelectorAll('[data-block="'+key+'"]').forEach(e => e.classList.remove('hot')));
}}
</script>
"""
    index_path = output / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    print(index_path)
    if args.open:
        webbrowser.open(index_path.as_uri())


if __name__ == "__main__":
    main()
