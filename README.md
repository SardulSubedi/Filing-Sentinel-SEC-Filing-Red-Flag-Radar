# Filing Sentinel — SEC Filing Red Flag Radar

**Filing Sentinel** is a research-oriented **SEC EDGAR anomaly scanner** for fundamental investors. It pulls **structured XBRL facts** and recent **10-K / 10-Q** filings, then runs **Benford’s Law forensics**, optional **semantic drift** on MD&A and Risk Factors, and an optional **Red Flag Report** (GPT with a deterministic fallback).

This software is for **informational and research purposes only** — not investment advice.

---

## Features

| Capability | What you get | API key |
|------------|----------------|---------|
| **Benford’s Law** | Expected vs observed digit distribution, deviation chart, MAD / χ² | None (SEC only) |
| **Semantic drift** | Similarity timeline and heatmap for MD&A / Risk Factors | OpenAI |
| **Red Flag Report** | Downloadable markdown brief with risk framing | OpenAI (optional) |

---

## Quick start

```powershell
cd filing-sentinel
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

**SEC compliance:** set a descriptive user-agent (see [Configuration](filing-sentinel/README.md#configuration-api-keys--compliance) in the app docs). **OpenAI** is optional; Benford analysis works without it.

---

## Documentation

- **[filing-sentinel/README.md](filing-sentinel/README.md)** — configuration, project layout, troubleshooting, security notes.

---

## Repository layout

```
.
├── README.md                    # Overview (this file — GitHub landing page)
├── filing-sentinel/             # Streamlit app and Python package
│   ├── README.md                # Detailed developer / operator reference
│   ├── app.py
│   ├── requirements.txt
│   ├── filing_sentinel/
│   └── .streamlit/
├── .agents/                     # Cursor agent skills (optional local tooling)
└── skills-lock.json
```

---

## Disclaimer

Data is sourced from **SEC EDGAR**. This project does not constitute financial, legal, or investment advice.
