"""SEC EDGAR API client for fetching company data and filings."""

import re
import time
from typing import Any

import requests

from .config import (
    RATE_LIMIT_DELAY,
    REQUEST_HEADERS,
    SEC_BASE_URL,
    SEC_TICKERS_URL,
)

_last_request_time = 0.0
_ticker_cache: dict[str, dict] | None = None


def _throttled_get(url: str, **kwargs: Any) -> requests.Response:
    """GET with SEC rate-limit compliance."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    resp = requests.get(url, headers=REQUEST_HEADERS, timeout=30, **kwargs)
    _last_request_time = time.time()
    resp.raise_for_status()
    return resp


def _load_ticker_map() -> dict[str, dict]:
    global _ticker_cache
    if _ticker_cache is not None:
        return _ticker_cache
    data = _throttled_get(SEC_TICKERS_URL).json()
    _ticker_cache = {}
    for entry in data.values():
        ticker = entry["ticker"].upper()
        _ticker_cache[ticker] = {
            "cik": entry["cik_str"],
            "name": entry["title"],
        }
    return _ticker_cache


def lookup_cik(ticker: str) -> tuple[str, str]:
    """Return (zero-padded CIK, company name) for a ticker symbol."""
    tmap = _load_ticker_map()
    key = ticker.upper().strip()
    if key not in tmap:
        raise ValueError(f"Ticker '{key}' not found in SEC EDGAR database.")
    entry = tmap[key]
    cik_padded = str(entry["cik"]).zfill(10)
    return cik_padded, entry["name"]


def get_company_facts(cik: str) -> dict:
    """Fetch all XBRL-reported financial facts for a company.

    Returns the full JSON from the company-facts API, which contains
    every numeric value the company has ever reported in structured form.
    """
    url = f"{SEC_BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
    return _throttled_get(url).json()


def get_submissions(cik: str) -> dict:
    """Fetch filing submission metadata (accession numbers, dates, types)."""
    url = f"{SEC_BASE_URL}/submissions/CIK{cik}.json"
    return _throttled_get(url).json()


def get_10k_10q_filings(cik: str, max_filings: int = 20) -> list[dict]:
    """Return metadata for recent 10-K and 10-Q filings, newest first."""
    subs = get_submissions(cik)
    recent = subs.get("filings", {}).get("recent", {})
    if not recent:
        return []

    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    results = []
    for i, form in enumerate(forms):
        if form in ("10-K", "10-Q") and i < len(dates):
            acc_clean = accessions[i].replace("-", "")
            doc_url = (
                f"https://www.sec.gov/Archives/edgar/data"
                f"/{cik.lstrip('0')}/{acc_clean}/{primary_docs[i]}"
            )
            results.append({
                "form": form,
                "date": dates[i],
                "accession": accessions[i],
                "url": doc_url,
            })
            if len(results) >= max_filings:
                break
    return results


def fetch_filing_html(url: str) -> str:
    """Download the raw HTML of a filing document."""
    resp = _throttled_get(url)
    return resp.text


def extract_all_xbrl_values(company_facts: dict) -> list[dict]:
    """Pull every reported numeric value from company facts.

    Returns a flat list of dicts with keys: concept, value, period, form, filed.
    """
    values = []
    facts = company_facts.get("facts", {})
    for taxonomy, concepts in facts.items():
        for concept_name, concept_data in concepts.items():
            units = concept_data.get("units", {})
            for unit_type, entries in units.items():
                for entry in entries:
                    val = entry.get("val")
                    if val is not None and isinstance(val, (int, float)) and val != 0:
                        values.append({
                            "taxonomy": taxonomy,
                            "concept": concept_name,
                            "value": val,
                            "unit": unit_type,
                            "period_end": entry.get("end", entry.get("instant", "")),
                            "form": entry.get("form", ""),
                            "filed": entry.get("filed", ""),
                        })
    return values
