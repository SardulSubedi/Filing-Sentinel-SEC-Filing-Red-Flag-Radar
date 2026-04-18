import os
from dotenv import load_dotenv

load_dotenv()

SEC_BASE_URL = "https://data.sec.gov"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
SEC_EFTS_URL = "https://efts.sec.gov/LATEST"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "FilingSentinel research@filingsentinel.dev",
)

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}

RATE_LIMIT_DELAY = 0.12  # SEC allows 10 req/s; ~120ms gap is safe

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o"
