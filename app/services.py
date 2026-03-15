from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from playwright.async_api import async_playwright

from app.models import ProductCard, SearchResponse, SearchResult
from app.scraper import search_easy, search_sodimac
from app.scraper.utils import similarity_score

logger = logging.getLogger(__name__)

StoreScraper = Callable[..., Awaitable[list[ProductCard]]]


async def _run_store_scraper(scraper: StoreScraper, product_name: str) -> list[ProductCard]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            results = await scraper(page, product_name)
            await context.close()
            await browser.close()
            return results
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scraper failed for %s: %s", scraper.__name__, exc)
        return []


async def search_all_stores(product_name: str) -> SearchResponse:
    scrapers: tuple[StoreScraper, ...] = (search_easy, search_sodimac)

    scraped_results = await asyncio.gather(
        *(_run_store_scraper(scraper, product_name) for scraper in scrapers)
    )

    ranked: list[SearchResult] = []
    for items in scraped_results:
        for item in items:
            score = similarity_score(product_name, item.name)
            if score <= 70:
                continue
            ranked.append(
                SearchResult(
                    store=item.store,
                    name=item.name,
                    price=item.price,
                    similarity=score,
                )
            )

    ranked.sort(key=lambda result: result.similarity, reverse=True)
    return SearchResponse(query=product_name, results=ranked)
