---
name: markup
description: Parse and extract from HTML and XML — BeautifulSoup selectors, parser choice, encodings, and the XML namespace maze (ElementTree). Use for "scrape this page", "extract data from this HTML", "parse this XML", or any markup a regex is about to be aimed at.
derivation: original
flow: util
domain: data
---

# markup

```bash
pip install beautifulsoup4 lxml
```

## HTML (BeautifulSoup)

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_bytes, "lxml")       # pass BYTES; bs4 sniffs the encoding
for row in soup.select("table#results tr"):    # CSS selectors: select()/select_one()
    cells = [td.get_text(strip=True) for td in row.select("td")]
link = soup.select_one("a.next")
href = link["href"] if link else None          # missing attr on a Tag raises KeyError
```

- **Parser choice changes results** on malformed HTML: `"lxml"` (fast, lenient), `"html.parser"` (stdlib, slower, sometimes different tree). Pin one; don't let environments differ.
- `get_text(strip=True)` collapses the whitespace mess; raw `.string` is None the moment an element has children.
- Don't regex HTML — nesting breaks every pattern eventually; that instinct is the trigger for this skill.

## XML (ElementTree) — the namespace maze

```python
import xml.etree.ElementTree as ET

root = ET.parse("feed.xml").getroot()
ns = {"a": "http://www.w3.org/2005/Atom"}          # map prefix -> URI yourself
for entry in root.findall("a:entry", ns):
    title = entry.findtext("a:title", namespaces=ns)
```

- **A namespaced document makes bare `findall("entry")` return nothing** — the #1 "my XML parse is empty" bug. Tags are really `{uri}entry`; supply the ns map or match the `{uri}tag` form.
- Namespace prefixes in the file (`atom:`, `ns0:`) are arbitrary — match on URIs via your own map, never on the file's prefixes.
- Attributes are usually un-namespaced even in namespaced docs; `el.get("id")` works as-is.
- Huge XML: `ET.iterparse(path, events=("end",))` + `elem.clear()` after processing — constant memory.

## Choosing
HTML in the wild → BeautifulSoup. Well-formed XML → ElementTree (stdlib) or lxml for XPath. JSON hiding in a `<script>` tag → extract the tag text, then `json.loads` — don't parse JS with a markup parser.
