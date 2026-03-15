from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Query

from app.models import SearchResponse
from app.services import search_all_stores

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chile Retail Product Search API", version="1.0.0")


@app.get("/search", response_model=SearchResponse)
async def search_products(
    product_name: str = Query(..., min_length=2, description="Product name to search"),
) -> SearchResponse:
    try:
        return await search_all_stores(product_name)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Unexpected error while searching") from exc
