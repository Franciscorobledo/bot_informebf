# Chile Retail Product Search API

Production-ready FastAPI API to search products in Chilean retail stores (`Easy.cl` and `Sodimac.cl`) and return best price/name matches ranked by similarity.

## Stack

- Python 3.11
- FastAPI
- Playwright
- RapidFuzz
- Pydantic
- Uvicorn
- HTTPX

## Project structure

```text
app/
 ├── main.py
 ├── scraper/
 │     ├── easy.py
 │     ├── sodimac.py
 │     └── utils.py
 ├── models.py
 └── services.py
```

## Endpoint

### `GET /search`

**Query parameter**
- `product_name` (required)

Example:

```bash
curl "http://localhost:8000/search?product_name=Taladro Bosch 18V"
```

Example response:

```json
{
  "query": "Taladro Bosch 18V",
  "results": [
    {
      "store": "easy",
      "name": "Taladro Percutor Bosch 18V Brushless",
      "price": "129990",
      "similarity": 92
    }
  ]
}
```

## Behavior

- Performs asynchronous scraping for each store.
- Extracts product name + price from cards.
- Computes similarity using `rapidfuzz.token_set_ratio`.
- Returns only matches with similarity `> 70`.
- Sorts descending by similarity.
- Includes per-store error isolation and API-level exception handling.

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

2. Run server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
