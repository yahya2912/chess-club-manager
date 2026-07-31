-- ============================================================
-- 01_schema.sql
-- Chess Club Tournament & Rating Manager
-- Full DDL: 7 tables, mapped 1:1 from proposal.tex Section 3
-- ============================================================

-- --------------------------------------------------------
-- player
-- --------------------------------------------------------
CREATE TABLE player (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    birth_year    INTEGER,
    current_elo   INTEGER NOT NULL DEFAULT 1000
);

-- --------------------------------------------------------
-- opening
-- --------------------------------------------------------
CREATE TABLE opening (
    eco_code      VARCHAR(3) PRIMARY KEY,
    name          TEXT NOT NULL
);

-- --------------------------------------------------------
-- tournament
-- --------------------------------------------------------
CREATE TABLE tournament (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    start_date    DATE NOT NULL,
    num_rounds    INTEGER NOT NULL CHECK (num_rounds > 0),
    status        TEXT NOT NULL DEFAULT 'planned'
                  CHECK (status IN ('planned', 'ongoing', 'closed'))
);

-- --------------------------------------------------------
-- registration
-- --------------------------------------------------------
CREATE TABLE registration (
    player_id     INTEGER NOT NULL REFERENCES player(id),
    tournament_id INTEGER NOT NULL REFERENCES tournament(id),
    seed          INTEGER,
    final_rank    INTEGER,
    PRIMARY KEY (player_id, tournament_id)
);

-- --------------------------------------------------------
-- round
-- --------------------------------------------------------
CREATE TABLE round (
    id            SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournament(id),
    round_no      INTEGER NOT NULL,
    CONSTRAINT round_tournament_no_unique UNIQUE (tournament_id, round_no)
);

-- --------------------------------------------------------
-- game
-- --------------------------------------------------------
CREATE TABLE game (
    id            SERIAL PRIMARY KEY,
    round_id      INTEGER NOT NULL REFERENCES round(id),
    white_id      INTEGER NOT NULL REFERENCES player(id),
    black_id      INTEGER NOT NULL REFERENCES player(id),
    eco_code      VARCHAR(3) NOT NULL REFERENCES opening(eco_code),
    result        TEXT NOT NULL,
    CONSTRAINT game_result_valid CHECK (result IN ('1-0', '0-1', '1/2-1/2')),
    CONSTRAINT game_distinct_players CHECK (white_id <> black_id)
);

-- --------------------------------------------------------
-- rating_history
-- --------------------------------------------------------
CREATE TABLE rating_history (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER NOT NULL REFERENCES player(id),
    valid_from    TIMESTAMP NOT NULL DEFAULT now(),
    elo           INTEGER NOT NULL
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX game_eco_idx ON game (eco_code);
CREATE INDEX game_round_idx ON game (round_id);
CREATE INDEX rating_history_player_time_idx
    ON rating_history (player_id, valid_from DESC);
CREATE INDEX registration_tournament_idx ON registration (tournament_id);
