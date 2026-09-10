# Chess Club Tournament & Rating Manager — User Manual

**Module:** Introduction to Database Management Systems · THGA Bochum  
**Author:** Yahya El Idrissi

## 1. Overview

The **Chess Club Tournament & Rating Manager** is a desktop application for managing chess-club tournaments and Elo ratings.

You can use it to:

- create players;
- create tournaments and rounds;
- register players;
- record game results;
- update Elo ratings automatically;
- view rating history;
- view standings with Buchholz tiebreaks.

The application has six tabs: **Players**, **Standings**, **Rating History**, **Record Game**, **Register Player**, and **Create Tournament**.

Normal workflow:

**Create players → Create tournament → Register players → Record games → Check standings and rating history.**

## 2. Setup and starting the application

### Requirements

Install:

- Docker Desktop or Docker Engine with Docker Compose;
- Python 3;
- Git, if the repository must be cloned.

Create `.env` in the repository root from `.env.example`:

```env
POSTGRES_USER=chess
POSTGRES_PASSWORD=change-me
POSTGRES_DB=chessdb
POSTGRES_TEST_DB=chessdb_test
POSTGRES_PORT=5432
API_KEY=change-me
```

### Start the backend

From the repository root, start **PostgreSQL and FastAPI together**:

```bash
docker compose up -d --build
```

Check that the API is running by opening:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### Start the frontend from source

**Linux / macOS:**

```bash
PYTHONPATH="$PWD/frontend" python3 -m chess_club_fe.main
```

**Windows PowerShell:**

```powershell
$env:PYTHONPATH="$PWD\frontend"
py -m chess_club_fe.main
```

A startup dialog asks for:

- **API URL** — for local use: `http://127.0.0.1:8000`
- **X-API-Key** — enter the `API_KEY` value from `.env`

The dialog checks the connection before the main application opens.

### Linux helper and Debian package

On Debian/Ubuntu Linux, the helper script can start the backend and source frontend:

```bash
./scripts/run-local.sh
```

If the Debian package is installed, launch the frontend with:

```bash
chess-club-manager
```

The PostgreSQL and FastAPI containers must already be running. The same startup connection dialog is used.

## 3. Using the application

### Players

Open **Players** to view existing players or click **Add Player** to create one. Enter a name, optional birth year, and initial Elo. The default Elo is `1000`. Creating a player also creates its first rating-history entry.

### Create Tournament

Open **Create Tournament**, enter a name, start date in `YYYY-MM-DD` format, and the number of rounds. The application creates the tournament and all round records automatically.

After creation, the generated round IDs are shown, for example:

```text
Rounds: R1=#1, R2=#2
```

Keep these IDs because **Record Game** uses the database round ID.

### Register Player

Open **Register Player**, choose a player and tournament, optionally enter a seed, and click **Register**. Both players must be registered before their game can be recorded. Duplicate registration is blocked.

### Record Game

Open **Record Game** and enter the round ID, White player, Black player, ECO code, and result. Valid results are `1-0`, `0-1`, and `1/2-1/2`.

A successful game immediately updates both Elo ratings and creates two rating-history entries.

Available ECO codes in the supplied reference data are:

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

Open **Rating History** to show all Elo-history rows or filter by player.

## 4. Functional verification

| Function | Test | Expected result |
| --- | --- | --- |
| Create player | Add Alice with Elo 1500 | Player and initial history entry appear |
| Create tournament | Create one-round Club Open | Tournament and one round are created |
| Register player | Register Alice and Bob | Both registrations succeed; duplicates are rejected |
| Record game | Alice beats Bob | Game is saved and both Elo ratings change |
| Rating history | Open Alice | Initial and updated Elo values are visible |
| Standings | Open Club Open | Points, results, and Buchholz are displayed |

If these checks succeed, the complete core workflow works from the user's perspective.

## 5. Troubleshooting

**Cannot reach API:** run `docker compose ps`, then check `http://127.0.0.1:8000/health`.

**Connection dialog rejects the key:** use the exact `API_KEY` value from `.env`.

**Docker command fails:** make sure Docker is running, then retry `docker compose up -d --build`.

**Player not registered:** register both players before recording their game.

**Unknown round ID:** use one of the IDs shown after tournament creation.

**Unknown ECO code:** use one of the ECO codes listed above.

The delivered version intentionally does not include automatic pairing generation, edit/delete GUI operations, automatic tournament closing, user accounts, or detailed opening analytics.
