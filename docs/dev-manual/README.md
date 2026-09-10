# Chess Club Tournament & Rating Manager — Developer Manual

**Module:** Introduction to Database Management Systems · THGA Bochum  
**Author:** Yahya El Idrissi

## 1. Architecture

```text
tkinter desktop frontend (.deb)
        ↓ HTTP + X-API-Key
FastAPI container
        ↓ psycopg
PostgreSQL 16 container
```

Docker Compose orchestrates **both backend services**: PostgreSQL and FastAPI. The frontend is not containerized and never accesses PostgreSQL directly. At startup it asks the user for the API URL and `X-API-Key` and keeps those values only for the current process.

Main repository areas:

```text
api/                    FastAPI application, Dockerfile and tests
db/                     PostgreSQL schema and seed data
frontend/chess_club_fe/  tkinter desktop application
frontend/debian/         Debian package files and build script
docs/                    proposal and manuals
scripts/                 local helper script
.github/workflows/       CI and release automation
Makefile                 builds all documentation PDFs into out/
```

## 2. Database design

`db/01_schema.sql` contains seven tables: `player`, `opening`, `tournament`, `registration`, `round`, `game`, and `rating_history`.

Important integrity rules include primary/foreign keys, composite registration key `(player_id, tournament_id)`, unique `(tournament_id, round_no)`, valid result values, distinct White/Black players, and controlled tournament status values. Indexes support game, registration, and rating-history lookups.

`db/02_seed.sql` contains deterministic reference/sample data used by CI.

## 3. Backend API and business logic

The FastAPI entry point is `api/app/main.py`. `/health` is public; application routes require `X-API-Key`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/players` | List players |
| POST | `/players` | Create player + initial history |
| GET | `/tournaments` | List tournaments |
| POST | `/tournaments` | Create tournament + all rounds |
| POST | `/registrations` | Register player |
| POST | `/games` | Record game + update Elo |
| GET | `/rating-history` | Read Elo history |
| GET | `/standings?tournament_id=...` | Calculate standings/Buchholz |
| GET | `/health` | Health check |

Multi-row writes are transactional. Player creation writes the player and first history row. Tournament creation writes the tournament and all rounds. Game recording validates round/registration, inserts the game, updates both ratings, and inserts two history rows; an exception rolls the transaction back.

Elo logic is isolated in `api/app/elo.py` with K=20. Standings use SQL CTEs; scoring is win=1, draw=0.5, loss=0, and full Buchholz is the sum of opponents' tournament points.

## 4. Frontend

The tkinter frontend has six tabs: Players, Standings, Rating History, Record Game, Register Player, and Create Tournament.

`api_client.py` is the only frontend HTTP layer. `main.py` opens a startup connection dialog for API URL + key, calls the API to validate them, and only then shows the main application. Write operations refresh dependent views.

## 5. Build, run and package

Create configuration:

```bash
cp .env.example .env
```

Start the backend:

```bash
docker compose up -d --build
```

Verify it:

```bash
curl http://127.0.0.1:8000/health
```

Start the source frontend:

```bash
PYTHONPATH="$PWD/frontend" python3 -m chess_club_fe.main
```

For Debian packaging:

```bash
sh frontend/debian/build-deb.sh
```

The generated package is `frontend/debian/chess-club-manager_1.0.0_all.deb`. The installed frontend still uses the startup connection dialog; PostgreSQL and FastAPI run as Docker Compose backend services.

## 6. Tests, CI and documentation build

Local API tests:

```bash
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt
api/.venv/bin/pip install -r api/requirements-dev.txt
cd api
.venv/bin/pytest tests -v
```

Build all documentation PDFs:

```bash
make all
```

The `Makefile` writes the proposal, User Manual, and Developer Manual PDFs to `out/`.

GitHub Actions verifies:

- database schema and deterministic seed data;
- API endpoint/business-logic tests;
- Docker Compose startup of PostgreSQL + FastAPI;
- Debian package creation;
- Makefile-driven LaTeX builds.

On a pushed tag matching `v*`, the workflow also creates a GitHub Release and attaches the generated PDFs.

## 7. How to add a new function

A new feature should follow the existing layers:

1. Decide whether persistent data/schema changes are required; preserve keys, constraints, and indexes.
2. Add or extend a FastAPI route and reuse the API-key dependency for application data.
3. Use a transaction whenever one action changes multiple rows.
4. Extend `frontend/chess_club_fe/api_client.py`; never access PostgreSQL from tkinter.
5. Add the GUI control/tab and refresh affected read views after writes.
6. Add tests for success, authentication, and important invalid cases.
7. Run pytest, Compose smoke test, packaging, and documentation CI.
8. Update User Manual, Developer Manual, and README.

Example: a future tournament-close feature would need backend validation/state transition, an API-client method, frontend action, tests for allowed/disallowed transitions, and documentation.

## 8. Possible extensions

Reasonable future work includes tournament closing controls, edit/delete workflows, automatic pairing generation, richer opening/player analytics, improved round selection, and role-based users. These are intentionally outside the delivered scope.

## 9. Reflection

The separation between database, API, and GUI made the project easier to test and reason about: database rules could be verified independently, API behavior could be tested before GUI work, and frontend changes did not require direct SQL access. The most important consistency-sensitive operation is game recording because one action affects the game table, two current Elo values, and two history rows; keeping that operation transactional prevents partial updates.

The delivery setup also became part of the design: containerizing both backend services makes the runtime reproducible, while keeping the frontend outside Docker matches the required desktop deployment model.

## 10. Sources and reuse

Course patterns were reused and adapted where appropriate, especially the PostgreSQL/FastAPI separation, `X-API-Key` protection, Docker Compose backend structure, and tkinter frontend approach. These patterns follow the DBMS lecture/exercise architecture, in particular the material around FastAPI, Docker Compose, API-key protection, and tkinter frontend packaging. Project-specific schema, Elo logic, standings/Buchholz queries, tournament workflow, tests, and documentation were developed for this chess-club application.

When adding third-party code in the future, document the exact source and what was adapted.
