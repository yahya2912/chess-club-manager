-- ============================================================
-- 02_seed.sql
-- Chess Club Tournament & Rating Manager
-- Seed data using real top-6 FIDE classical ratings (August 2026)
-- Elo deltas computed at K=20 for exact white/black symmetry
-- ============================================================

-- --------------------------------------------------------
-- player  (current_elo = real FIDE classical rating, Aug 2026)
-- --------------------------------------------------------
INSERT INTO player (name, birth_year, current_elo) VALUES
    ('Magnus Carlsen',    1990, 2823),  -- id 1
    ('Fabiano Caruana',   1992, 2792),  -- id 2
    ('Hikaru Nakamura',   1987, 2792),  -- id 3
    ('Javokhir Sindarov', 2005, 2777),  -- id 4
    ('Vincent Keymer',    2004, 2767),  -- id 5
    ('Wesley So',         1993, 2765);  -- id 6

-- --------------------------------------------------------
-- opening
-- --------------------------------------------------------
INSERT INTO opening (eco_code, name) VALUES
    ('B01', 'Scandinavian Defense'),
    ('C50', 'Italian Game'),
    ('D02', 'London System'),
    ('E60', 'King''s Indian Defense'),
    ('A00', 'Irregular Opening'),
    ('C00', 'French Defense');

-- --------------------------------------------------------
-- tournament  (ongoing: 2 of 3 rounds played)
-- --------------------------------------------------------
INSERT INTO tournament (name, start_date, num_rounds, status) VALUES
    ('August Invitational 2026', '2026-08-01', 3, 'ongoing');  -- id 1

-- --------------------------------------------------------
-- registration  (seed = rank by pre-tournament FIDE rating, final_rank NULL: not closed)
-- --------------------------------------------------------
INSERT INTO registration (player_id, tournament_id, seed, final_rank) VALUES
    (1, 1, 1, NULL),  -- Carlsen
    (2, 1, 2, NULL),  -- Caruana
    (3, 1, 3, NULL),  -- Nakamura
    (4, 1, 4, NULL),  -- Sindarov
    (5, 1, 5, NULL),  -- Keymer
    (6, 1, 6, NULL);  -- So

-- --------------------------------------------------------
-- round
-- --------------------------------------------------------
INSERT INTO round (tournament_id, round_no) VALUES
    (1, 1),  -- id 1
    (1, 2);  -- id 2

-- --------------------------------------------------------
-- game
-- Round 1: Carlsen vs So, Caruana vs Nakamura, Sindarov vs Keymer
-- Round 2: Carlsen vs Sindarov, Caruana vs Keymer, Nakamura vs So
-- (no repeated pairings across the two rounds)
-- --------------------------------------------------------
INSERT INTO game (round_id, white_id, black_id, eco_code, result) VALUES
    (1, 1, 6, 'B01', '1-0'),      -- Carlsen bt So
    (1, 2, 3, 'C50', '1/2-1/2'),  -- Caruana drew Nakamura
    (1, 4, 5, 'D02', '1-0'),      -- Sindarov bt Keymer
    (2, 1, 4, 'E60', '1-0'),      -- Carlsen bt Sindarov
    (2, 2, 5, 'A00', '1-0'),      -- Caruana bt Keymer
    (2, 3, 6, 'C00', '1/2-1/2');  -- Nakamura drew So

-- --------------------------------------------------------
-- rating_history
-- Deltas computed at K=20 against real Aug-2026 ratings,
-- rounded to nearest integer, symmetric per game.
-- --------------------------------------------------------
INSERT INTO rating_history (player_id, valid_from, elo) VALUES
    -- baseline, pre-tournament (real Aug 2026 FIDE ratings)
    (1, '2026-07-01 00:00:00', 2823),
    (2, '2026-07-01 00:00:00', 2792),
    (3, '2026-07-01 00:00:00', 2792),
    (4, '2026-07-01 00:00:00', 2777),
    (5, '2026-07-01 00:00:00', 2767),
    (6, '2026-07-01 00:00:00', 2765),

    -- after round 1 (2026-08-01)
    (1, '2026-08-01 18:00:00', 2831),  -- +8  (beat So)
    (6, '2026-08-01 18:00:00', 2757),  -- -8
    (2, '2026-08-01 18:00:00', 2792),  -- +0  (drew Nakamura, near-equal ratings)
    (3, '2026-08-01 18:00:00', 2792),  -- +0
    (4, '2026-08-01 18:00:00', 2787),  -- +10 (beat Keymer)
    (5, '2026-08-01 18:00:00', 2757),  -- -10

    -- after round 2 (2026-08-08)
    (1, '2026-08-08 18:00:00', 2840),  -- +9  (beat Sindarov)
    (4, '2026-08-08 18:00:00', 2778),  -- -9
    (2, '2026-08-08 18:00:00', 2801),  -- +9  (beat Keymer)
    (5, '2026-08-08 18:00:00', 2748),  -- -9
    (3, '2026-08-08 18:00:00', 2791),  -- -1  (drew So, slight favorite)
    (6, '2026-08-08 18:00:00', 2758);  -- +1

-- --------------------------------------------------------
-- player.current_elo updated to reflect state after round 2
-- --------------------------------------------------------
UPDATE player SET current_elo = 2840 WHERE id = 1;  -- Carlsen
UPDATE player SET current_elo = 2801 WHERE id = 2;  -- Caruana
UPDATE player SET current_elo = 2791 WHERE id = 3;  -- Nakamura
UPDATE player SET current_elo = 2778 WHERE id = 4;  -- Sindarov
UPDATE player SET current_elo = 2748 WHERE id = 5;  -- Keymer
UPDATE player SET current_elo = 2758 WHERE id = 6;  -- So
