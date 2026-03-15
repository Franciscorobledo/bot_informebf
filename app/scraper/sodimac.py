from __future__ import annotations

from playwright.async_api import Page

from app.models import ProductCard
from app.scraper.utils import build_search_url, normalize_price

SODIMAC_BASE_URL = "https://www.sodimac.cl/sodimac-cl/search"


async def search_sodimac(page: Page, product_name: str) -> list[ProductCard]:
    url = build_search_url(SODIMAC_BASE_URL, product_name, "Ntt")
    await page.goto(url, wait_until="domcontentloaded", timeout=45000)
    await page.wait_for_timeout(2000)

    product_cards: list[ProductCard] = []
    selectors = [
        "[data-testid='product-pod']",
        "[data-testid='product-card']",
        ".search-results .pod",
        "article",
    ]

    for selector in selectors:
        elements = await page.query_selector_all(selector)
        if not elements:
            continue

        for element in elements:
            name_node = await element.query_selector(
                "[data-testid='product-title'], .product-name, h2, h3, a"
            )
            price_node = await element.query_selector(
                "[data-testid='price-main'], .price, [class*='price']"
            )
            if not name_node or not price_node:
                continue

            name = (await name_node.inner_text()).strip()
            price_raw = (await price_node.inner_text()).strip()
            price = normalize_price(price_raw)
            if not name or not price:
                continue

            product_cards.append(ProductCard(store="sodimac", name=name, price=price))

        if product_cards:
            break

    return product_cards
