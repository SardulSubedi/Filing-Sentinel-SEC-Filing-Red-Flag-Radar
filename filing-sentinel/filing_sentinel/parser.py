"""Extract structured text sections from SEC filing HTML documents."""

import re

from bs4 import BeautifulSoup


# Patterns that match common section headers in 10-K / 10-Q filings.
# Each tuple is (section_key, start_patterns, stop_patterns).
SECTION_PATTERNS: list[tuple[str, list[str], list[str]]] = [
    (
        "mda",
        [
            r"(?:item\s*(?:2|7)[\.\s]*[—\-:]*\s*)"
            r"management['']?s?\s+discussion\s+and\s+analysis",
        ],
        [
            r"item\s*(?:3|7a|8)[\.\s]*[—\-:]*\s*",
            r"quantitative\s+and\s+qualitative\s+disclosures?\s+about\s+market\s+risk",
            r"financial\s+statements?\s+and\s+supplementary\s+data",
        ],
    ),
    (
        "risk_factors",
        [
            r"item\s*1a[\.\s]*[—\-:]*\s*risk\s+factors",
        ],
        [
            r"item\s*1b[\.\s]*[—\-:]*\s*",
            r"item\s*2[\.\s]*[—\-:]*\s*",
            r"unresolved\s+staff\s+comments",
            r"propert(?:y|ies)",
        ],
    ),
]


def _html_to_text(html: str) -> str:
    """Convert filing HTML to clean plain text."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(["script", "style", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_section(html: str, section_key: str) -> str | None:
    """Extract a named section (e.g. 'mda', 'risk_factors') from filing HTML.

    Uses regex anchors on the plain-text version of the filing to locate
    the start and end of each section.
    """
    text = _html_to_text(html)
    if not text:
        return None

    patterns = {k: (starts, stops) for k, starts, stops in SECTION_PATTERNS}
    if section_key not in patterns:
        return None

    starts, stops = patterns[section_key]

    start_idx = None
    for pat in starts:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            start_idx = match.start()
            break
    if start_idx is None:
        return None

    search_after = start_idx + 50
    end_idx = len(text)
    for pat in stops:
        match = re.search(pat, text[search_after:], re.IGNORECASE)
        if match:
            candidate = search_after + match.start()
            if candidate < end_idx:
                end_idx = candidate

    section = text[start_idx:end_idx].strip()

    if len(section) < 200:
        return None

    max_chars = 80_000
    if len(section) > max_chars:
        section = section[:max_chars] + "\n\n[...truncated...]"

    return section


def extract_financial_numbers(html: str) -> list[float]:
    """Pull all dollar/numeric values from filing text for Benford's analysis.

    Supplements XBRL data by scanning the raw text for numbers that might
    not appear in structured data (footnotes, narrative disclosures).
    """
    text = _html_to_text(html)

    patterns = [
        r"\$\s*([\d,]+(?:\.\d+)?)\s*(?:million|billion|thousand)?",
        r"([\d,]+(?:\.\d+)?)\s+(?:million|billion|thousand)",
    ]

    numbers = []
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            raw = match.group(1).replace(",", "")
            try:
                val = float(raw)
                if val > 0:
                    numbers.append(val)
            except ValueError:
                continue
    return numbers
