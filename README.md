# Photo Explorer

A Flask web application for browsing and searching a curated photo gallery. Photos are stored in MySQL with associated keywords and color metadata. An ETL pipeline loads tab-separated CSV datasets into the database, and the UI provides keyword search with live autocomplete suggestions.

## Features

- **Photo gallery** — Grid layout showing up to 20 photos on the home page, with hover descriptions and a fullscreen modal on click.
- **Keyword search** — Submit a keyword via the search bar to filter photos whose tags contain that text.
- **Autocomplete** — As you type, `/suggest_keywords` returns matching keywords as clickable badges (300 ms debounce).
- **ETL pipeline** — Extracts tab-delimited CSV files from `data/`, transforms rows into model fields, and loads them into MySQL.
- **Service layer** — `PhotoService` and `KeywordService` isolate database queries from Flask routes for easier testing.
- **Automated tests** — Pytest covers services and HTTP routes using an in-memory SQLite database.
- **Docker support** — Containerized deployment with a production-ready `Dockerfile`.
- **CI/CD pipeline** — Jenkins runs linting, SAST (Bandit, Safety), unit tests, Trivy image scanning, and DAST (OWASP ZAP).

## Project Structure

```
Project/
├── app.py              # Flask application and route definitions
├── config.py           # Database URI, secret key, and data directory settings
├── models.py           # SQLAlchemy models: Photo, Keyword, Color
├── services.py         # PhotoService and KeywordService (business logic)
├── etl_service.py      # ETL pipeline (extract, transform, load)
├── import_data.py      # CLI entry point: create tables + run ETL
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image for deployment
├── Jenkinsfile         # CI/CD pipeline (build, test, security scans)
├── pytest.ini          # Pytest configuration
├── data/               # Source CSV files (gitignored; not included in repo)
│   ├── photos.csv000
│   ├── keywords.csv000
│   └── colors.csv000
├── templates/
│   └── index.html      # Gallery UI, search form, modal, autocomplete JS
├── static/
│   └── style.css       # Layout, hero section, gallery grid, modal styles
└── tests/
    ├── conftest.py     # Adds project root to sys.path
    ├── test_services.py
    └── test_routes.py
```

## Architecture

```mermaid
flowchart TB
    subgraph ui [Web UI]
        HTML[index.html]
        CSS[style.css]
    end

    subgraph flask [Flask App]
        Routes[app.py routes]
        Services[services.py]
    end

    subgraph data_layer [Data Layer]
        Models[models.py]
        MySQL[(MySQL)]
    end

    subgraph etl [ETL]
        CSV[data/*.csv000]
        ETL[etl_service.py]
        Import[import_data.py]
    end

    HTML --> Routes
    Routes --> Services
    Services --> Models
    Models --> MySQL
    CSV --> ETL
    ETL --> Models
    Import --> ETL
```

### Data Model

| Table      | Purpose                                      | Key fields                          |
|-----------|----------------------------------------------|-------------------------------------|
| `photos`  | Image metadata and URL                       | `photo_id`, `image_url`, `description`, `width`, `height`, `username` |
| `keywords`| Searchable tags linked to a photo            | `photo_id` (FK), `keyword`          |
| `colors`  | Dominant colors per photo                    | `photo_id` (FK), `hex`, `color_name`|

### API Routes

| Method   | Path               | Description                                      |
|----------|--------------------|--------------------------------------------------|
| `GET`    | `/`                | Show gallery (latest 20 photos)                  |
| `POST`   | `/`                | Search photos by keyword (form field `keyword`)  |
| `GET`    | `/suggest_keywords`| JSON autocomplete; query param `q`               |

## Prerequisites

- Python 3.11+
- MySQL 8.0 (local or Docker)
- Source CSV files placed in the `data/` directory (see [Data files](#data-files))

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure the database

Create a MySQL database named `photo_app`, then set the connection string if needed:

```bash
export SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:password@localhost/photo_app"
export SECRET_KEY="your-secret-key"
```

Defaults are defined in `config.py` (`mysql+pymysql://root@localhost/photo_app`).

### 3. Load data

Place the three tab-separated CSV files in `data/`, then run:

```bash
python import_data.py
```

This creates tables and runs the full ETL pipeline.

### 4. Run the application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Data Files

The ETL pipeline expects tab-delimited CSV files (extension `.csv000`) under `data/`:

| File               | Expected columns (among others)                          |
|--------------------|----------------------------------------------------------|
| `photos.csv000`    | `photo_id`, `photo_image_url`, `photo_description`, `photo_width`, `photo_height`, `photographer_username` |
| `keywords.csv000`  | `photo_id`, `keyword`                                    |
| `colors.csv000`    | `photo_id`, `hex`, `keyword` (used as color name)        |

The `data/` directory is gitignored; obtain the dataset separately and place the files locally before running `import_data.py`.

## Running Tests

Tests use in-memory SQLite and do not require MySQL:

```bash
pytest -v
```

Coverage includes:

- `PhotoService.get_all_photos` (default and custom limits)
- `PhotoService.search_by_keyword`
- `KeywordService.suggest`
- HTTP routes (`/`, `/suggest_keywords`)

## Docker

Build and run the container:

```bash
docker build -t photo-app .
docker run -p 5000:5000 \
  -e SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:password@host.docker.internal/photo_app" \
  photo-app
```

For production, use `flask run --host=0.0.0.0` (as in the Jenkinsfile) instead of the debug server in `app.py`.

## CI/CD (Jenkins)

The `Jenkinsfile` defines a pipeline that:

1. Checks out the repository
2. Starts MySQL on a Docker network
3. Installs dependencies and runs Bandit + Safety scans
4. Builds and pushes a Docker image to Docker Hub
5. Runs pytest against MySQL on `localhost:3306`
6. Scans the image with Trivy
7. Deploys the app container and runs OWASP ZAP baseline DAST

Artifacts archived: `zap-report.html`, `bandit-report.json`, `safety-report.txt`.

## Environment Variables

| Variable                 | Default                                      | Description                    |
|--------------------------|----------------------------------------------|--------------------------------|
| `SQLALCHEMY_DATABASE_URI`| `mysql+pymysql://root@localhost/photo_app`   | MySQL connection string        |
| `SECRET_KEY`             | `supersecretkey`                             | Flask session signing key      |
