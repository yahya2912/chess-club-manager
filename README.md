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

Automatic pairing generation is intentionally outside the project scope.

## Architecture

```text
tkinter desktop frontend
        ↓ HTTP + X-API-Key
FastAPI backend
        ↓ psycopg
PostgreSQL 16
```

**Stack:** PostgreSQL 16 · FastAPI · Python/tkinter · Docker Compose · pytest · LaTeX · GitHub Actions

## Repository Structure

```text
api/                    FastAPI backend and automated tests
db/                     PostgreSQL schema and seed data
frontend/chess_club_fe/  tkinter desktop frontend
frontend/debian/         Debian package files and build script
docs/                    proposal, User Manual and Developer Manual
scripts/                 local development launcher
.github/workflows/       continuous integration
```

## Quick Start

Create the local configuration:

```bash
cp .env.example .env
```

Create the Python environment:

```bash
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt
```

On Debian/Ubuntu Linux, start the local application from the repository root with:

```bash
./scripts/run-local.sh
```

The script starts PostgreSQL, FastAPI and the tkinter frontend.

The main target environment is Linux. For macOS and Windows startup instructions, see the [User Manual](docs/user-manual/README.md).

A running backend can be checked at:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Testing

Install the development requirements and run the API test suite:

```bash
api/.venv/bin/pip install -r api/requirements-dev.txt
cd api
../api/.venv/bin/pytest tests -v
```

GitHub Actions automatically verifies:

- PostgreSQL schema and deterministic seed data
- database acceptance checks
- FastAPI endpoint and business-logic tests
- compilation of the LaTeX proposal, User Manual and Developer Manual

## Debian Package

On a Debian-based Linux system, build the frontend package with:

```bash
sh frontend/debian/build-deb.sh
```

Output:

```text
frontend/debian/chess-club-manager_1.0.0_all.deb
```

The Debian package contains the desktop frontend. PostgreSQL and the FastAPI backend remain separate runtime components.

## Documentation

- [Project Proposal](docs/proposal.tex)
- [User Manual](docs/user-manual/README.md)
- [User Manual — LaTeX](docs/user-manual/user-manual.tex)
- [Developer Manual](docs/dev-manual/README.md)
- [Developer Manual — LaTeX](docs/dev-manual/dev-manual.tex)

The CI workflow compiles the LaTeX documents and uploads the generated PDFs as workflow artifacts.

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
