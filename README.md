# SF 311 Citizen Service Requests — Local Analytics Pipeline

> End-to-end analytics pipeline that ingests **7.6 M** SF 311 records (2008–2025), loads them into PostgreSQL with **dbt**, and delivers interactive insights via **Metabase** — all orchestrated with Docker Compose.

---

## ✨ Key Findings

- **Demand keeps climbing**  
  Annual volume rose steadily since 2018, peaking at **808 K** requests in 2023 (+ 19.6 % YoY).

- **Bulky-item pick-ups & General cleaning dominate**  
  Together they account for nearly **50 %** of all service requests.

- **Mission & South of Market lead by a wide margin**  
  The Mission logged **711 K** requests, 43 % more than the next busiest neighborhood.

<p align="center">
  <img src="Photo/request_volume.png" alt="Yearly requests" width="45%" />
  <img src="Photo/top_10_complaint_types.png.png"  alt="Top-10 subtypes"  width="25%" />
  <img src="requests_per_thousand_residents.png"   alt="Neighborhood ranking" width="25%" />
</p>

---

## Table of Contents

1. [Key Findings](#✨-key-findings)  
2. [Architecture](#architecture)  
3. [Tech Stack](#tech-stack)  
4. [Quick Start](#quick-start)  
5. [Repository Structure](#repository-structure)  
6. [Implementation Details](#implementation-details)  
7. [Future Extensions](#future-extensions)

```
```
## Architecture

```
Socrata API ──► Local disk (CSV → Parquet)
                 │
                 ▼
      PostgreSQL (raw.sf311)
                 │
        dbt models (staging → mart)
                 │
         Metabase dashboards
```

*Docker Compose* spins up **Postgres 15** and **Metabase** containers; everything else is pure Python.

---

## Tech Stack

| Layer | Tooling | Rationale |
|-------|---------|-----------|
| **Extraction** | `requests`, `pandas` | Simple one-time snapshot; API supports CSV export. |
| **Load** | `pyarrow ➜ gzip CSV` + `psql COPY` | Fastest path to insert 7 M rows locally. |
| **Warehouse** | **PostgreSQL 15** | Familiar SQL engine; supports extensions if geo needed. |
| **Transformation / Modeling** | **dbt-postgres v1.9** | Version-controlled SQL, lineage graph, tests. |
| **BI / Dashboards** | **Metabase** | OSS, Docker-ready, quick chart building. |
| **Orchestration** | *none for MVP* | Single-run pipeline; daily incremental left as future work. |

---

## Quick Start
<sup><sub>*Requires Docker & Python ≥ 3.9*</sub></sup>

```bash
git clone https://github.com/<you>/SF311.git
cd SF311

# 1 Download snapshot + basic EDA (creates data/ and Parquet)
python -m jupyter nbconvert --to notebook --execute notebooks/01_data_download_and_eda.ipynb

# 2 Spin up Postgres & Metabase
docker compose up -d postgres metabase

# 3 Load snapshot into Postgres (≈ 5 min)
python notebooks/02_load_to_postgres.py     # reads data/sf311_snapshot.parquet

# 4 Build dbt models
cd sf311           # dbt project folder
dbt run            # materialises staging & mart schemas

# 5 Open dashboard
open http://localhost:3000                  # Metabase → host=postgres user=sf311 pw=sf311

```

---

## Repository Structure

| Path | Purpose / Notes |
|------|-----------------|
| `data/` *(git-ignored)* | raw CSV, Parquet snapshot, temp gzip (large files, private) |
| `notebooks/` | `01_data_download_and_eda.ipynb`, `02_load_to_postgres.py` |
| `sf311/` | dbt project (`models/staging`, `models/dimensions`, `models/marts`, `analyses/queries.sql`) |
| `Photo/` | Dashboard PNGs referenced in README |
| `docker-compose.yml` | Postgres 15 + Metabase latest |
| `.gitignore` | excludes `data/`, `logs/`, `sf311/target/`, Docker volumes |

*All secrets (dbt profile) remain in your home directory or environment variables*

---

## Implementation Details

1. **Snapshot download**  
   `01_data_download_and_eda.ipynb` grabs a 700 MB CSV via Socrata, converts to Parquet, performs quick EDA, and saves to `data/`.

2. **Bulk load**  
   `02_load_to_postgres.py` converts Parquet ⇒ gzip CSV and executes a `COPY` into `raw.sf311` (≈ 2 min insert).

3. **Modeling with dbt**  

   | Model | Schema | Purpose |
   |-------|--------|---------|
   | `stg_sf311` | `staging` | cleans & type-casts core columns |
   | `dim_date`  | `mart` | calendar dimension via `generate_series` |
   | `dim_neighborhood` | `mart` | request counts by neighborhood |
   | `fct_requests` | `mart` | fact table with year/month & status flags |

4. **Metabase visualisation**  
   - Connects to Postgres service name `postgres` (internal network).  
   - Three saved questions feed a public dashboard (see screenshots).

---

## Future Extensions

*listed but intentionally out-of-scope for this MVP*

- Incremental sync script (`src/load_incremental.py`) running daily via cron / GitHub Actions  
- PostGIS & Mapbox heat-map of request density  
- dbt tests (`unique`, `not_null`, `accepted_values`) and `dbt docs` site  
- CI workflow that runs `black`, `dbt build`, and Metabase smoke tests on PRs

---


**Thank you for visiting this project.** If you have any questions or suggestions, feel free to open an issue or submit a pull request.
