# Chess Club Tournament & Rating Manager — Developer Manual

**Module:** Introduction to Database Management Systems · THGA Bochum  
**Author:** Yahya El Idrissi

## 1. Architecture

The application uses a simple three-layer architecture:

```text
tkinter desktop frontend
        ↓ HTTP + X-API-Key
FastAPI backend
        ↓ psycopg
PostgreSQL 16
```

The frontend never accesses PostgreSQL directly. All reads and writes go through the FastAPI backend. PostgreSQL runs through Docker Compose for local development.

Main repository areas:

```text
api/                    FastAPI application and tests
db/                     PostgreSQL schema and seed data
frontend/chess_club_fe/  tkinter desktop application
frontend/debian/         Debian package files and build script
docs/                    proposal and manuals
scripts/                 local helper scripts
.github/workflows/       GitHub Actions CI
```

Configuration comes from `.env`. Important values are the PostgreSQL connection settings and `API_KEY`. The frontend uses `CHESS_API_URL` and `CHESS_API_KEY`.

## 2. Database design

The schema is defined in `db/01_schema.sql` and contains seven tables:

| Table | Purpose |
| --- | --- |
| `player` | Player identity and current Elo |
| `opening` | ECO opening reference data |
| `tournament` | Tournament metadata and status |
| `registration` | Many-to-many relation between players and tournaments |
| `round` | Rounds belonging to tournaments |
| `game` | Recorded games, players, result and ECO code |
| `rating_history` | Historical Elo values for each player |

Important database constraints include:

- primary and foreign keys for entity relationships;
- composite primary key `(player_id, tournament_id)` to prevent duplicate registrations;
- unique `(tournament_id, round_no)` values;
- valid game results limited to `1-0`, `0-1`, and `1/2-1/2`;
- White and Black must be different players;
- tournament status limited to `planned`, `ongoing`, or `closed`.

Indexes support common lookups on game rounds/openings, tournament registrations, and rating history by player and time.

`db/02_seed.sql` supplies reproducible sample data used by CI. It is separate from normal runtime data.

## 3. Backend API

The backend entry point is `api/app/main.py`. `/health` is a public diagnostic endpoint. All application routers require the `X-API-Key` HTTP header; a missing or incorrect key returns HTTP 401.

Application endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/players` | List players |
| POST | `/players` | Create player and initial rating history |
| GET | `/tournaments` | List tournaments |
| POST | `/tournaments` | Create tournament and all rounds |
| POST | `/registrations` | Register a player for a tournament |
| POST | `/games` | Record a game and update Elo |
| GET | `/rating-history` | Read rating history, optionally by player |
| GET | `/standings?tournament_id=...` | Calculate tournament standings |
| GET | `/health` | Backend health check |

### Transactional writes

Operations that must stay consistent are executed in database transactions.

Creating a player inserts both the `player` row and its initial `rating_history` row. Creating a tournament inserts the tournament and every required round. Recording a game validates the round and registrations, inserts the game, updates both current Elo values, and inserts two rating-history rows. If an exception occurs, the connection helper rolls the transaction back.

### Elo calculation

Elo logic is isolated in `api/app/elo.py` and uses a fixed **K-factor of 20**.

Expected score follows the standard Elo logistic formula:

```text
E = 1 / (1 + 10^((opponent_rating - rating) / 400))
```

The updated rating is:

```text
new_rating = old_rating + round(20 × (actual_score - expected_score))
```

A recorded game updates Elo immediately. The calculation is kept separate from database access so it can be unit-tested independently.

### Standings and Buchholz

The standings endpoint calculates its result directly from stored registrations and games using SQL common table expressions (CTEs).

Scoring is:

- win = 1 point;
- draw = 0.5 points;
- loss = 0 points.

Full Buchholz is the sum of the tournament points of all opponents a player has faced. Final ordering is by points, Buchholz, wins, then player name.

## 4. Frontend

The desktop frontend is written with Python tkinter. `frontend/chess_club_fe/main.py` creates one notebook window with six tabs:

- **Players**
- **Standings**
- **Rating History**
- **Record Game**
- **Register Player**
- **Create Tournament**

`api_client.py` is a thin HTTP client built with Python's standard `urllib` library. It sends `X-API-Key` with API requests and converts backend errors into `ApiError` exceptions for the GUI.

Successful write operations trigger refresh callbacks so dependent read views show new players, tournaments, Elo values and standings without restarting the application.

The frontend intentionally does not implement automatic pairing generation, edit/delete CRUD, or tournament-closing controls.

## 5. Local development

### Prepare configuration

From the repository root:

```bash
cp .env.example .env
```

Create the backend environment:

```bash
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt
api/.venv/bin/pip install -r api/requirements-dev.txt
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

On Linux, the helper script can start the local stack:

```bash
./scripts/run-local.sh
```

For manual development, load `.env`, run Uvicorn from `api/`, then start the frontend with `frontend` on `PYTHONPATH`. The User Manual contains OS-specific startup examples for Linux, macOS and Windows.

### Database initialization

Docker Compose mounts `db/` into PostgreSQL's initialization directory. On a brand-new database volume, the schema and seed scripts are executed automatically.

To apply them manually to a database, use `psql` with:

```bash
psql ... -f db/01_schema.sql
psql ... -f db/02_seed.sql
```

Do not delete or empty `02_seed.sql` simply to create a clean local demo database because CI depends on the deterministic seed dataset.

## 6. Tests and continuous integration

API tests are stored in `api/tests/`. They cover read endpoints, authentication, player/tournament creation, registration validation, game recording, Elo updates, rating history, standings and Buchholz invariants.

Run the API tests locally with the development dependencies installed:

```bash
cd api
pytest tests -v
```

GitHub Actions is defined in `.github/workflows/ci.yml` and runs on pushes and pull requests to `main`. It contains three jobs:

1. **Database schema + seed smoke test** — starts PostgreSQL 16, applies schema and seed data, checks expected row counts and an Elo-symmetry acceptance criterion.
2. **pytest API endpoint tests** — runs the Python API test suite against PostgreSQL.
3. **Compile LaTeX documentation** — compiles `docs/proposal.tex` and uploads the resulting PDF artifact.

A green CI run therefore verifies the core database setup, backend behavior and proposal compilation. GUI interaction itself is verified manually.

## 7. Debian packaging

The frontend can be packaged as a Debian `.deb` file on a Debian-based Linux system:

```bash
sh frontend/debian/build-deb.sh
```

The generated package is:

```text
frontend/debian/chess-club-manager_1.0.0_all.deb
```

The package contains the desktop frontend. PostgreSQL and the FastAPI backend remain separate runtime services and must be available for the GUI to function.

## 8. Scope and maintenance notes

The delivered project focuses on database-backed tournament and rating management. Its supported core workflow is:

```text
create players
→ create tournament and rounds
→ register players
→ record games
→ update Elo/history
→ calculate standings
```

Known non-goals are automatic Swiss pairing, edit/delete GUI operations, user accounts, automatic tournament closing, and detailed opening/color analytics.

When extending the project, preserve the existing database constraints and transactional behavior. New API endpoints should use the existing API-key dependency when they expose application data, and database changes should be accompanied by tests and CI-safe migration/schema updates.
