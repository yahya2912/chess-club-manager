# Chess Club Tournament & Rating Manager

![CI](https://github.com/yahya2912/chess-club-manager/actions/workflows/ci.yml/badge.svg)

Term project for **Introduction to Database Management Systems** at **THGA Bochum**.  
Author: **Yahya El Idrissi** · Summer Term 2026

A self-hosted desktop application for managing chess-club tournaments and Elo ratings. It stores players, tournaments, registrations, rounds, games, openings and rating history in PostgreSQL and provides a tkinter GUI backed by a FastAPI API.

## Features

- Create players with an initial Elo rating
- Create tournaments and automatically create their rounds
- Register players for tournaments
- Record game results with ECO opening codes
- Update both players' Elo ratings immediately after a game
- Store and view Elo rating history
- Calculate tournament standings with points and Buchholz tiebreaks
- Protect application API routes with an `X-API-Key`
- Configure the API URL and key through a startup connection dialog

Automatic pairing generation is intentionally outside the project scope.

## Architecture

```text
tkinter desktop frontend (.deb)
        ↓ HTTP + X-API-Key
FastAPI container
        ↓ psycopg
PostgreSQL 16 container
```

Docker Compose orchestrates the backend services (PostgreSQL + FastAPI). The frontend runs separately as a desktop application and never accesses PostgreSQL directly.

**Stack:** PostgreSQL 16 · FastAPI · Python/tkinter · Docker Compose · pytest · LaTeX · GitHub Actions

## Repository Structure

```text
api/                    FastAPI backend, Dockerfile and automated tests
db/                     PostgreSQL schema and seed data
frontend/chess_club_fe/  tkinter desktop frontend
frontend/debian/         Debian package files and build script
docs/                    proposal, User Manual and Developer Manual
scripts/                 local development launcher
.github/workflows/       continuous integration and release automation
Makefile                 builds all documentation PDFs into out/
```

## Quick Start

Create the local configuration:

```bash
cp .env.example .env
```

Start the complete backend:

```bash
docker compose up -d --build
```

Check the API:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Start the source frontend:

```bash
PYTHONPATH="$PWD/frontend" python3 -m chess_club_fe.main
```

At startup, enter the API URL (for local use: `http://127.0.0.1:8000`) and the `API_KEY` value from `.env`.

On Debian/Ubuntu Linux, `./scripts/run-local.sh` starts the containerized backend and then launches the frontend. For macOS and Windows instructions, see the [User Manual](docs/user-manual/README.md).

## Testing

Create a development environment and run the API test suite:

```bash
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt
api/.venv/bin/pip install -r api/requirements-dev.txt
cd api
.venv/bin/pytest tests -v
```

GitHub Actions automatically verifies:

- PostgreSQL schema and deterministic seed data
- database acceptance checks
- FastAPI endpoint and business-logic tests
- Docker Compose startup of PostgreSQL + FastAPI
- Debian frontend package creation
- Makefile-driven compilation of the LaTeX proposal, User Manual and Developer Manual

## Documentation Build

Requirement: `latexmk` and a suitable TeX Live/MacTeX installation.

Build all PDFs from the repository root:

```bash
make all
```

The PDFs are written to `out/`. Use `make clean` for auxiliary files or `make distclean` to remove the complete output directory.

Pushing a version tag matching `v*` runs CI and creates a GitHub Release containing the generated documentation PDFs.

## Debian Package

On a Debian-based Linux system, build the frontend package with:

```bash
sh frontend/debian/build-deb.sh
```

Output:

```text
frontend/debian/chess-club-manager_1.0.0_all.deb
```

The package contains the desktop frontend. The PostgreSQL and FastAPI backend services are started separately with Docker Compose.

## Documentation

- [Project Proposal](docs/proposal.tex)
- [User Manual](docs/user-manual/README.md)
- [User Manual — LaTeX](docs/user-manual/user-manual.tex)
- [Developer Manual](docs/dev-manual/README.md)
- [Developer Manual — LaTeX](docs/dev-manual/dev-manual.tex)

## Project Scope

The delivered core workflow is:

```text
Create players
→ Create tournament and rounds
→ Register players
→ Record games
→ Update Elo and rating history
→ View standings
```

The final version does not include automatic Swiss pairing, edit/delete operations through the GUI, user accounts, automatic tournament closing or detailed opening analytics.
