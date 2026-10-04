#!/usr/bin/env python3
"""Write index.html: one card for every book folder here (a folder with a book.json),
and for each book kept in its own repo and listed in elsewhere.json.

    python3 build_index.py

elsewhere.json is a list of those books' folders, relative to this one (e.g.
"../maqasid"); their book.json is read from there, so they need a domain.

The page is built from each book's book.json: title (ar, en), about_book (en),
domain. Optional keys read if present: "tile" (the short Arabic word on the
card, default the title's first word) and "repo" (a Source link).
A book with a domain links there; otherwise to its folder.
"""

import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
TEMPLATE = HERE / "index.template.html"


def blurb(book: dict) -> str:
    text = re.sub(r"<[^>]+>", "", " ".join(book["about_book"]["en"][:1]))
    if len(text) <= 230:
        return text
    cut = text[:230]
    # a sentence end, not an abbreviation such as "(d. 790)"
    ends = [m.start() for m in re.finditer(r"(?<=\w\w\w)[.;] ", cut)]
    end = ends[-1] if ends else -1
    return (cut[: end + 1] if end > 80 else cut.rsplit(" ", 1)[0] + "…")


def card(folder: Path, book: dict) -> str:
    title = book["title"]
    tile = book.get("tile") or title["ar"].split()[0]
    url = f"https://{book['domain']}/" if book.get("domain") else f"{folder.name}/"
    label = f"{book['domain']} →" if book.get("domain") else "Read the book →"
    source = f'\n      <a class="src" href="{html.escape(book["repo"])}">Source</a>' if book.get("repo") else ""
    return f"""  <article class="site">
    <div class="top">
      <div class="tile" aria-hidden="true">{html.escape(tile)}</div>
      <div class="names"><p class="ar" lang="ar">{html.escape(title['ar'])}</p><h2>{html.escape(title['en'])}</h2></div>
    </div>
    <p class="kind">Book</p>
    <p class="desc">{html.escape(blurb(book))}</p>
    <div class="links">
      <a class="visit" href="{html.escape(url)}">{html.escape(label)}</a>{source}
    </div>
  </article>
"""


def main() -> None:
    paths = list(HERE.glob("*/book.json"))
    elsewhere = HERE / "elsewhere.json"
    if elsewhere.exists():
        paths += [HERE / folder / "book.json" for folder in json.loads(elsewhere.read_text(encoding="utf-8"))]
    books = sorted((p.parent.resolve(), json.loads(p.read_text(encoding="utf-8"))) for p in paths)
    for folder, book in books:
        if folder.parent != HERE.resolve() and not book.get("domain"):
            raise SystemExit(f"{folder}: a book in another repo needs a domain in its book.json")
    cards = "\n".join(card(folder, book) for folder, book in books)
    page = TEMPLATE.read_text(encoding="utf-8").replace("<!--CARDS-->", cards)
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"index.html: {len(books)} book(s): {', '.join(f.name for f, _ in books)}")


if __name__ == "__main__":
    main()
