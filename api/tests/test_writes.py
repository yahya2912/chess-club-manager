"""Tests for write endpoints (POST /registrations, POST /games) and Elo maths.

Elo unit tests hit no database. Endpoint tests mutate data, so each cleans up
the rows it creates and asserts on before/after deltas rather than absolute
counts -- so they don't disturb the read-endpoint tests regardless of order.
"""
import psycopg

from app import config
from app.elo import new_ratings, expected_score


def test_elo_equal_players_win():
    assert new_ratings(1500, 1500, "1-0") == (1510, 1490)


def test_elo_symmetry_holds_for_all_results():
    for result in ("1-0", "0-1", "1/2-1/2"):
        for w, b in [(1500, 1500), (1800, 1400), (1400, 1800), (2000, 1234)]:
            nw, nb = new_ratings(w, b, result)
            assert (nw - w) + (nb - b) == 0, (w, b, result)


def test_elo_expected_scores_sum_to_one():
    assert round(expected_score(1600, 1400) + expected_score(1400, 1600), 6) == 1.0


def test_elo_rejects_bad_result():
    try:
        new_ratings(1500, 1500, "win")
        assert False, "expected ValueError"
    except ValueError:
        pass


def _connect():
    return psycopg.connect(
        host=config.POSTGRES_HOST, port=config.POSTGRES_PORT,
        dbname=config.POSTGRES_DB, user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
    )


def _get_elo(player_id):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_elo FROM player WHERE id = %s", (player_id,))
            return cur.fetchone()[0]


def _cleanup_game(game_id, white_id, black_id, restore):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM rating_history
                WHERE id IN (
                    SELECT id FROM rating_history
                    WHERE player_id IN (%s, %s)
                    ORDER BY valid_from DESC LIMIT 2
                )
                """,
                (white_id, black_id),
            )
            cur.execute("DELETE FROM game WHERE id = %s", (game_id,))
            for pid, elo in restore.items():
                cur.execute("UPDATE player SET current_elo = %s WHERE id = %s",
                            (elo, pid))
        conn.commit()


def test_registration_requires_key(client):
    resp = client.post("/registrations",
                       json={"player_id": 1, "tournament_id": 1})
    assert resp.status_code == 401


def test_registration_duplicate_conflicts(client, auth):
    resp = client.post("/registrations", headers=auth,
                       json={"player_id": 1, "tournament_id": 1})
    assert resp.status_code == 409


def test_game_requires_key(client):
    resp = client.post("/games", json={
        "round_id": 2, "white_id": 5, "black_id": 6,
        "eco_code": "C50", "result": "1-0"})
    assert resp.status_code == 401


def test_game_same_player_rejected(client, auth):
    resp = client.post("/games", headers=auth, json={
        "round_id": 2, "white_id": 1, "black_id": 1,
        "eco_code": "C50", "result": "1-0"})
    assert resp.status_code == 400


def test_game_bad_result_rejected(client, auth):
    resp = client.post("/games", headers=auth, json={
        "round_id": 2, "white_id": 1, "black_id": 2,
        "eco_code": "C50", "result": "win"})
    assert resp.status_code == 400


def test_game_unregistered_player_rejected(client, auth):
    resp = client.post("/games", headers=auth, json={
        "round_id": 2, "white_id": 1, "black_id": 99,
        "eco_code": "C50", "result": "1-0"})
    assert resp.status_code == 409


def test_game_records_and_updates_elo_symmetrically(client, auth):
    white_id, black_id = 5, 6
    before_w = _get_elo(white_id)
    before_b = _get_elo(black_id)

    resp = client.post("/games", headers=auth, json={
        "round_id": 2, "white_id": white_id, "black_id": black_id,
        "eco_code": "C50", "result": "1-0"})
    assert resp.status_code == 201
    body = resp.json()

    try:
        after_w = body["elo_changes"]["white"]["after"]
        after_b = body["elo_changes"]["black"]["after"]
        assert (after_w - before_w) + (after_b - before_b) == 0
        assert after_w > before_w
        assert _get_elo(white_id) == after_w
        assert _get_elo(black_id) == after_b
    finally:
        _cleanup_game(body["id"], white_id, black_id,
                      restore={white_id: before_w, black_id: before_b})

    assert _get_elo(white_id) == before_w
    assert _get_elo(black_id) == before_b
