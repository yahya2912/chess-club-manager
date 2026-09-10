# Chess Club Tournament & Rating Manager — User Manual

**Module:** Introduction to Database Management Systems · THGA Bochum  
**Author:** Yahya El Idrissi

## 1. Overview

The **Chess Club Tournament & Rating Manager** is a small desktop application for managing chess-club tournaments and Elo ratings.

You can use it to:

- create players;
- create tournaments and their rounds;
- register players for tournaments;
- record game results;
- update Elo ratings automatically;
- view rating history;
- view tournament standings with Buchholz tiebreaks.

The application has six tabs: **Players**, **Standings**, **Rating History**, **Record Game**, **Register Player**, and **Create Tournament**.

The normal workflow is:

**Create players → Create tournament → Register players → Record games → Check standings and rating history.**

## 2. Setup and starting the application

### What you need

Before running the project, install:

- **Docker Desktop** or Docker Engine with Docker Compose;
- **Python 3**;
- **Git** if you want to clone the repository.

The project also needs a `.env` file in the repository root. Create it from `.env.example` and keep the same structure:

```env
POSTGRES_USER=chess
POSTGRES_PASSWORD=change-me
POSTGRES_DB=chessdb
POSTGRES_TEST_DB=chessdb_test
POSTGRES_PORT=5432
API_KEY=change-me
```

For a first source-based setup, create the Python virtual environment and install the API requirements.

**Linux / macOS:**

```bash
python3 -m venv api/.venv
api/.venv/bin/pip install -r api/requirements.txt
```

**Windows PowerShell:**

```powershell
py -m venv api/.venv
.\api\.venv\Scripts\pip install -r api\requirements.txt
```

### Linux (Debian / Ubuntu)

Linux is the main target environment.

From the repository root, the easiest option is:

```bash
./scripts/run-local.sh
```

This starts PostgreSQL, FastAPI, and the tkinter frontend.

If the Debian package is installed, the frontend can also be started with:

```bash
chess-club-manager
```

The database and API must already be running in that case.

### macOS

On macOS, run the components manually.

First Terminal window:

```bash
cd /path/to/chess-club-manager
docker compose up -d postgres
set -a
source .env
set +a
api/.venv/bin/uvicorn app.main:app --app-dir api --host 127.0.0.1 --port 8000
```

Keep that Terminal window open.

Then open a second Terminal window:

```bash
cd /path/to/chess-club-manager
export CHESS_API_URL="http://127.0.0.1:8000"
export CHESS_API_KEY="$(grep '^API_KEY=' .env | cut -d= -f2-)"
PYTHONPATH="$PWD/frontend" python3 -m chess_club_fe.main
```

The **Chess Club Manager** window should open.

### Windows

On Windows, use **PowerShell** and Docker Desktop.

First PowerShell window:

```powershell
cd C:\path\to\chess-club-manager
docker compose up -d postgres
$env:POSTGRES_USER="chess"
$env:POSTGRES_PASSWORD="change-me"
$env:POSTGRES_DB="chessdb"
$env:POSTGRES_PORT="5432"
$env:API_KEY="change-me"
.\api\.venv\Scripts\uvicorn app.main:app --app-dir api --host 127.0.0.1 --port 8000
```

Use the same values as in your `.env` file. Keep this window open.

Then open a second PowerShell window:

```powershell
cd C:\path\to\chess-club-manager
$env:CHESS_API_URL="http://127.0.0.1:8000"
$env:CHESS_API_KEY="change-me"
$env:PYTHONPATH="$PWD\frontend"
py -m chess_club_fe.main
```

Again, `CHESS_API_KEY` must match `API_KEY` from `.env`.

### Quick backend check

Before opening the GUI, you can visit:

```text
http://127.0.0.1:8000/health
```

A working backend returns:

```json
{"status":"ok"}
```

## 3. Using the application

### Players

Open **Players** to view existing players or click **Add Player** to create one.

Enter a name, optional birth year, and initial Elo. The default Elo is `1000`. Creating a player also creates the first rating-history entry automatically.

### Create Tournament

Open **Create Tournament**, enter a name, start date in `YYYY-MM-DD` format, and the number of rounds. The application creates the tournament and all round records automatically.

After creation, it shows the generated round IDs, for example:

```text
Rounds: R1=#1, R2=#2
```

Keep these IDs because **Record Game** asks for the round ID.

### Register Player

Open **Register Player**, choose a player and tournament, optionally enter a seed, and click **Register**.

Both players must be registered before their game can be recorded. The same player cannot be registered twice for the same tournament.

### Record Game

Open **Record Game** and enter:

- Round ID;
- White player;
- Black player;
- ECO code;
- result: `1-0`, `0-1`, or `1/2-1/2`.

A successful game immediately updates both Elo ratings and creates two new rating-history entries.

Available ECO codes in the supplied database are:

| Code | Opening |
| --- | --- |
| `A00` | Irregular Opening |
| `B01` | Scandinavian Defense |
| `C00` | French Defense |
| `C50` | Italian Game |
| `D02` | London System |
| `E60` | King's Indian Defense |

### Standings and Rating History

Open **Standings** and choose a tournament to see points, Buchholz, wins, draws, losses, and games played.

Open **Rating History** to see Elo values over time. You can show all players or select one player from the dropdown.

## 4. Simple first workflow

For a quick test of the whole application:

1. Create two players, for example **Alice** and **Bob**.
2. Create a one-round tournament called **Club Open**.
3. Note the generated round ID, for example `R1=#1`.
4. Register Alice and Bob for the tournament.
5. Record a game using round ID `1`, ECO code `C50`, and a result such as `1-0`.
6. Check **Players** to see the new Elo values.
7. Check **Rating History** for the new entries.
8. Check **Standings** for the tournament result.

If all three views update correctly, the full core workflow is working.

## 5. Troubleshooting

**The application cannot reach the API:** make sure FastAPI is running and check `http://127.0.0.1:8000/health`.

**Unauthorized / invalid API key:** make sure `CHESS_API_KEY` used by the frontend matches `API_KEY` used by the backend.

**Docker command fails:** make sure Docker Desktop or Docker Engine is running, then try `docker compose up -d postgres` again.

**Player not registered:** register both players for the tournament before recording their game.

**Unknown round ID:** use one of the round IDs shown when the tournament was created.

**Unknown ECO code:** use one of the ECO codes listed above.

**Player already registered:** the same player can only be registered once per tournament.

The delivered version intentionally does not include automatic pairing generation, editing/deleting records through the GUI, automatic tournament closing, or detailed opening statistics.
