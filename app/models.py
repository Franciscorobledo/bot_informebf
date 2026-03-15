from __future__ import annotations

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    store: str
    name: str
    price: str
    similarity: int = Field(ge=0, le=100)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class ProductCard(BaseModel):
    store: str
    name: str
    price: str
