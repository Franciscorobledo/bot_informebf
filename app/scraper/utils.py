from __future__ import annotations

import re
from urllib.parse import quote_plus

from rapidfuzz import fuzz


def build_search_url(base_url: str, query: str, param: str) -> str:
    return f"{base_url}?{param}={quote_plus(query)}"


def normalize_price(raw_price: str) -> str:
    digits = re.findall(r"\d+", raw_price.replace(".", ""))
    return "".join(digits) if digits else ""


def similarity_score(query: str, candidate: str) -> int:
    return int(fuzz.token_set_ratio(query, candidate))
