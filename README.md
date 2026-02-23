# Masters Scholarship Scraper (Python + Selenium)

This project provides a compliance-first, multi-source web scraper for scholarships where Master's eligibility is present.

## What it does

- Collects records from multiple source categories:
	- University scholarship pages
	- Government scholarship portals
	- NGO/Foundation scholarship portals
	- Scholarship aggregators
- Normalizes records into a single schema
- Filters to opportunities mentioning Master's/Postgraduate eligibility
- Deduplicates records
- Exports results to CSV in `data/exports`
- Writes run logs to `data/logs/scraper.log`

## Project structure

- `src/core`: schema, fetch client, throttling, policy, logging
- `src/adapters`: source-specific adapter modules
- `src/pipeline`: normalize + deduplicate logic
- `src/output`: CSV export
- `src/orchestrator.py`: end-to-end pipeline coordinator
- `src/run_once.py`: one-time execution
- `src/run_daily.py`: daily scheduler process

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Ensure Chrome and ChromeDriver are installed and compatible (for Selenium-enabled sources).

## Run

One-time run:

```powershell
python -m src.run_once
```

Daily scheduler (runs at 02:00 local time):

```powershell
python -m src.run_daily
```

## Source onboarding

Source loading is configuration-driven via `config/sources.json`.

Each category can contain multiple source URLs with:

- `name`: source label used in outputs
- `url`: listing page URL
- `dynamic`: `true` to use Selenium rendering
- `enabled`: `true` to include in runs

Adapters used:

- `src/adapters/university/adapter.py`
- `src/adapters/government/adapter.py`
- `src/adapters/ngo/adapter.py`
- `src/adapters/aggregator/adapter.py`

Adapter contract:

- Implement `collect(fetch_client)` and return `list[ScholarshipRecord]`
- Use `fetch_client.fetch_static(url)` for static pages
- Use `fetch_client.fetch_dynamic(url)` for JS-heavy pages
- Map extracted values into `ScholarshipRecord`

## Compliance-first notes

- Keep scraping to public pages and approved sources.
- Apply conservative request rates.
- Respect terms/robots and internal legal/compliance requirements.
- Maintain clear source attribution in exported data.

## Next implementation step

Populate `config/sources.json` with real approved sources and set `enabled: true` per source.
