# Fashion Studio ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen?logo=pytest&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-50%20passed-brightgreen?logo=pytest&logoColor=white)

An end-to-end **ETL (Extract, Transform, Load) pipeline** built with Python that scrapes fashion product data from [Fashion Studio](https://fashion-studio.dicoding.dev/), cleans and transforms it, then loads it into three destinations: a local CSV file, Google Sheets, and a PostgreSQL database.

> Final project for the **Fundamental Data Processing** course — [DBS Foundation Coding Camp 2026](https://www.dicoding.com/) powered by DBS Foundation in collaboration with Dicoding Indonesia (Data Scientist Learning Path) — scored **Advanced (Perfect Score)**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ETL PIPELINE                           │
│                                                             │
│  ┌──────────┐    ┌─────────────┐    ┌────────────────────┐ │
│  │ EXTRACT  │───▶│  TRANSFORM  │───▶│       LOAD         │ │
│  └──────────┘    └─────────────┘    └────────────────────┘ │
│                                              │              │
│  Web Scraping     Data Cleaning         ┌────┴────┐         │
│  (BeautifulSoup)  & Validation          │         │         │
│                   (Pandas)          ┌───▼───┐ ┌──▼──────┐  │
│                                     │  CSV  │ │ Google  │  │
│  Source:                            └───────┘ │ Sheets  │  │
│  fashion-studio                              └──────────┘  │
│  .dicoding.dev    USD → IDR             ┌──────────────┐   │
│  (50 pages)       conversion            │  PostgreSQL  │   │
│                   (×16,000)             └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11+ |
| Web Scraping | Requests, BeautifulSoup4 |
| Data Processing | Pandas, NumPy |
| Google Sheets | gspread, google-auth |
| Database | PostgreSQL, SQLAlchemy, psycopg2 |
| Testing | Pytest, unittest.mock |
| Environment | python-dotenv |
| Code Quality | Flake8, Black |

---

## Project Structure

```
fashion-etl-pipeline/
│
├── utils/
│   ├── __init__.py
│   ├── extract.py        # Web scraping logic
│   ├── transform.py      # Data cleaning & transformation
│   ├── load.py           # Load to CSV, Google Sheets, PostgreSQL
│   └── logger.py         # Centralized logging configuration
│
├── tests/
│   ├── test_extract.py   # Unit tests for extract module
│   ├── test_transform.py # Unit tests for transform module
│   └── test_load.py      # Unit tests for load module
│
├── .env.example          # Environment variables template
├── .gitignore
├── main.py               # ETL pipeline entry point
├── products.csv          # Output: local CSV result
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python **3.11** or higher
- PostgreSQL (local or cloud instance)
- A Google Cloud **Service Account** with Sheets and Drive API enabled
- A Google Sheets file shared with the service account

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/fashion-etl-pipeline.git
cd fashion-etl-pipeline
```

**2. Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Configuration

**1. Copy the environment template**
```bash
cp .env.example .env
```

**2. Fill in your values in `.env`**
```env
BASE_URL=https://fashion-studio.dicoding.dev/
JSON_KEY_PATH=your-service-account-key.json
SPREADSHEET_NAME=Your Spreadsheet Name
DB_URL=postgresql://username:password@host:5432/dbname
```

**3. Place your Google Service Account JSON key** in the project root and update `JSON_KEY_PATH` accordingly.

---

## How to Run

```bash
python main.py
```

The pipeline will log its progress to both the console and `etl_pipeline.log`:

```
2026-05-24 10:00:00 | INFO     | __main__       | Starting Extraction Stage...
2026-05-24 10:00:02 | INFO     | utils.extract  | Successfully extracted page 1. Total records: 20
...
2026-05-24 10:01:15 | INFO     | __main__       | ETL Pipeline Completed Successfully!
```

---

## Running Tests

**Run all unit tests**
```bash
pytest tests/ -v
```

**Run with coverage report**
```bash
coverage run -m pytest tests/
coverage report
```

Tests use `unittest.mock` to simulate HTTP requests and external services (Google Sheets, PostgreSQL) without real network calls.

---

## Data Pipeline Flow

### 1. Extract
- Scrapes up to **50 pages** of product listings from Fashion Studio
- Extracts 7 fields per product: `Title`, `Price`, `Rating`, `Colors`, `Size`, `Gender`, `Timestamp`
- Handles pagination automatically via "Next" button detection
- Returns raw data as a list of dictionaries

### 2. Transform
Applies the following cleaning steps in order:
1. Remove duplicate rows
2. Remove products with title `"Unknown Product"`
3. Convert `Price` from USD string → IDR float (× 16,000 exchange rate)
4. Extract numeric `Rating` from raw string (e.g., `"⭐ 4.5 / 5"` → `4.5`)
5. Extract integer `Colors` count (e.g., `"3 colors"` → `3`)
6. Strip label prefixes from `Size` and `Gender` columns
7. Drop rows with missing `Title`, `Price`, or `Rating`
8. Cast columns to correct data types (`int64`, `float64`)

### 3. Load
Cleaned data is saved to **three destinations simultaneously**:
- **CSV** — `products.csv` in the project root
- **Google Sheets** — Live spreadsheet via gspread API
- **PostgreSQL** — `products` table via SQLAlchemy

---

## Output

| Destination | Link / Location |
|---|---|
| Google Sheets | [View Live Data](https://docs.google.com/spreadsheets/d/1e63v9C4WNCPpNi7HAQ3jFmmIWoyDERLmoY6BV8AT9m4/edit?usp=sharing) |
| CSV | `products.csv` (generated locally after running) |
| PostgreSQL | Table: `products` in configured database |

**Sample output data:**

| Title | Price (IDR) | Rating | Colors | Size | Gender |
|---|---|---|---|---|---|
| T-shirt 2 | 1,634,400 | 3.9 | 3 | M | Women |
| Hoodie 3 | 7,950,080 | 4.8 | 3 | L | Unisex |
| Pants 4 | 7,476,960 | 3.3 | 3 | XL | Men |

---

## Challenges & Learnings

- **Pagination handling** — The website uses a custom URL pattern (`/page2`, `/page3`) rather than query parameters, which required careful URL construction logic.
- **Inconsistent HTML structure** — Some product cards had `Colors` as a standalone paragraph (e.g., `"3 Colors"`) without a colon separator, requiring a separate regex fallback in the parser.
- **Google Sheets API type compatibility** — NumPy integer and float types are not JSON-serializable by default, requiring a `safe_value()` converter before uploading rows.
- **Virtual environment naming conflict** — Learned that naming a venv `.env` conflicts with the dotenv file convention — always use `venv/` as the directory name.

---

## Achievement

This project was submitted as the **Final Project** for:

> **Fundamental Pemrosesan Data Course**
> DBS Foundation Coding Camp 2026
> Powered by DBS Foundation × Dicoding Indonesia
> Learning Path: **Data Scientist**

**Result: Advanced (5/5 Perfect Score)**

Mentor feedback highlighted strong implementation of:
- Complete ETL pipeline with 3 load destinations
- Comprehensive unit testing with mocking
- Clean, readable code structure

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with dedication by <a href="https://github.com/qasthalaani">Yasmin Qasthalani</a>
</p>
