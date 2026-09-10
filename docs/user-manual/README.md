# Chess Club Tournament & Rating Manager — User Manual

**Module:** Introduction to Database Management Systems · THGA Bochum  
**Author:** Yahya El Idrissi  
**Application:** Chess Club Tournament & Rating Manager

## 1. Purpose

The Chess Club Tournament & Rating Manager is a desktop application for managing the core data of a small chess club. It allows a user to create players and tournaments, register players for tournaments, record game results, maintain Elo ratings over time, and inspect tournament standings and rating history.

The application is intentionally focused on these core workflows. It does not generate chess pairings automatically and it does not provide edit/delete operations for existing records.

## 2. Starting the application

The desktop frontend requires the PostgreSQL database and FastAPI backend to be available. In a prepared source checkout on the intended Linux environment, the complete local stack can be started from the repository root with:

```bash
./scripts/run-local.sh
```

The script starts PostgreSQL with Docker Compose, starts the FastAPI backend on `http://127.0.0.1:8000`, and then opens the tkinter desktop application.

If the Debian package has already been installed and the backend is running, the frontend can be launched with:

```bash
chess-club-manager
```

The frontend reads its API configuration from environment variables. There is no connection dialog inside the application. The normal configuration variables are `CHESS_API_URL` and `CHESS_API_KEY`.

## 3. Main window

The main window is titled **Chess Club Manager** and contains six tabs:

1. **Players** — view the player list and create players.
2. **Standings** — select a tournament and view its current standings.
3. **Rating History** — view stored Elo values for all players or one selected player.
4. **Record Game** — enter a completed game and update both players' ratings.
5. **Register Player** — register an existing player for an existing tournament.
6. **Create Tournament** — create a tournament and automatically create its rounds.

The normal order of use is:

**Create players → Create tournament → Register players → Record games → Check standings and rating history.**

## 4. Players

Open the **Players** tab to view all players currently stored in the database. The table contains:

- **ID** — unique player identifier.
- **Name** — player's name.
- **Born** — birth year, if supplied.
- **Elo** — current Elo rating.

Players are returned in descending Elo order.

### 4.1 Creating a player

1. Click **Add Player**.
2. Enter the player's **Name**.
3. Enter a **Birth year** if desired.
4. Enter the player's **Initial Elo**. The default value is `1000`.
5. Click **Add Player** in the dialog.

A successful creation closes the dialog and adds the player to the player list. The application also creates the player's first rating-history entry automatically.

Validation rules include:

- Name is required.
- Birth year must be numeric if entered.
- Birth year must be between 1900 and the current year.
- Elo must be numeric and between 0 and 4000.

Use **Refresh** to reload the player table from the backend if necessary.

## 5. Create Tournament

Open the **Create Tournament** tab to create a new tournament.

The form contains:

- **Tournament name** — required name of the tournament.
- **Start date (YYYY-MM-DD)** — tournament start date.
- **Number of rounds** — total number of rounds, from 1 to 50.

The start-date field initially contains today's date and the rounds field initially contains `4`.

### 5.1 Creating a tournament

1. Enter the tournament name.
2. Verify or change the start date using `YYYY-MM-DD` format.
3. Enter the required number of rounds.
4. Click **Create Tournament**.

The tournament is created with status `planned`. All required round records are created automatically in the same operation.

After creation, the application displays the generated round IDs, for example:

```text
Tournament #1 created as planned.
Rounds: R1=#1, R2=#2, R3=#3
```

**Keep note of these round IDs.** The **Record Game** tab requires the database round ID when a game is entered.

## 6. Register Player

A player must be registered for the relevant tournament before that player can be used in a recorded tournament game.

Open the **Register Player** tab. The form contains:

- **Player** — existing player selected from a dropdown.
- **Tournament** — existing tournament selected from a dropdown.
- **Seed (optional)** — optional integer representing the player's tournament seed.

### 6.1 Registering a player

1. Select a player.
2. Select a tournament.
3. Optionally enter a seed.
4. Click **Register**.

The status line displays **Registered successfully.** after a successful registration.

Use **Refresh** if you want to reload both dropdowns manually. The dropdown data is also refreshed when new players or tournaments are created.

A player cannot be registered twice for the same tournament. Attempting this produces an error indicating that the player is already registered.

## 7. Record Game

Open the **Record Game** tab after both players have been registered for the tournament.

The form contains:

- **Round ID** — database ID of the round in which the game was played.
- **White** — player with the white pieces.
- **Black** — player with the black pieces.
- **ECO code** — opening code for the game.
- **Result** — one of `1-0`, `0-1`, or `1/2-1/2`.

The ECO field defaults to `C50` and the result defaults to `1-0`.

### 7.1 Recording a game

1. Enter the correct round ID shown when the tournament was created.
2. Select the White player.
3. Select the Black player.
4. Enter a valid ECO code.
5. Select the result.
6. Click **Record Game**.

When the game is accepted, it is stored in the database and both players' Elo ratings are recalculated immediately. The application reports the previous and new ratings, for example:

```text
Game #1 recorded.
White: 1500 -> 1510   Black: 1500 -> 1490
```

Two new rating-history entries are also written automatically, one for each player.

### 7.2 Available ECO reference codes

The supplied opening catalogue contains these codes:

| ECO code | Opening |
| --- | --- |
| `A00` | Irregular Opening |
| `B01` | Scandinavian Defense |
| `C00` | French Defense |
| `C50` | Italian Game |
| `D02` | London System |
| `E60` | King's Indian Defense |

The ECO code must already exist in the database. An unknown ECO code is rejected.

### 7.3 Game validation

The application refuses a game when, for example:

- the round ID is not a whole number;
- the round does not exist;
- White and Black are the same player;
- either player is not registered for the tournament containing that round;
- the ECO code does not exist;
- the result is invalid.

No Elo or game data is partially saved when the operation fails.

## 8. Standings

Open the **Standings** tab and select a tournament from the **Tournament** dropdown.

The table displays:

- **Player**
- **Points**
- **Buchholz**
- **W** — wins
- **D** — draws
- **L** — losses
- **Games** — games played

Points are calculated from the recorded results:

- win = 1 point;
- draw = 0.5 points;
- loss = 0 points.

Buchholz is calculated from the scores of a player's opponents and is used as a tiebreak value.

Standings are ordered by points, then Buchholz, then number of wins, and finally player name.

Use **Refresh** to reload the tournament list and standings. After successful write operations, the application also refreshes dependent read views automatically.

## 9. Rating History

Open the **Rating History** tab to inspect stored Elo values.

The table contains:

- **Player**
- **Elo**
- **Recorded at**

Use the **Player** dropdown to choose either:

- **All players**, or
- one individual player.

Every player receives an initial rating-history entry when created. Every successfully recorded game adds one new entry for White and one new entry for Black after their ratings are recalculated.

Use **Refresh** to reload the available players and history data.

## 10. Typical complete workflow

For a new tournament, use the application in this sequence:

1. Open **Players** and create all required players.
2. Open **Create Tournament** and create the tournament.
3. Note the generated round IDs.
4. Open **Register Player** and register each participant.
5. Open **Record Game** after a game has been completed.
6. Enter the correct round ID, players, ECO code and result.
7. Open **Players** to confirm updated current Elo values.
8. Open **Rating History** to confirm the new rating entries.
9. Open **Standings** to inspect points, results and Buchholz values.
10. Repeat the game-recording step for further games and rounds.

## 11. Common errors and solutions

### Cannot reach API

If the application reports that it cannot reach the API, verify that the FastAPI backend is running and that `CHESS_API_URL` points to the correct address.

### Unauthorized / invalid API key

The application endpoints require the correct API key. Verify the `CHESS_API_KEY` configuration and the backend `API_KEY` value.

### Player already registered

The same player can only be registered once per tournament. Choose another player or tournament.

### Player not registered in tournament

Both White and Black must first be registered for the tournament containing the selected round.

### Unknown round ID

Use one of the round IDs generated and displayed when the tournament was created.

### Unknown ECO code

Use an ECO code that exists in the application's opening catalogue.

## 12. Current application scope

The delivered version supports player creation, tournament creation with automatic round creation, player registration, game recording, automatic Elo updates, rating history and tournament standings with Buchholz.

The following functions are intentionally outside the delivered scope:

- automatic Swiss or other pairing generation;
- editing or deleting existing records through the GUI;
- changing tournament status through the GUI;
- automatic tournament closing;
- detailed statistics by colour or opening;
- user accounts or per-user permissions.

These limitations do not affect the core tournament and rating-management workflow described in this manual.
