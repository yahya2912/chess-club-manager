"""End-to-end tests for the four Week 2 read endpoints, plus auth.

Assertions are pinned to the committed seed data (top-6 FIDE players,
6 games, 18 rating_history rows). If the seed changes, update these.
"""


# ----------------------------------------------------------------------
# Health (unauthenticated)
# ----------------------------------------------------------------------
def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ----------------------------------------------------------------------
# Auth: every protected endpoint rejects missing and wrong keys with 401
# ----------------------------------------------------------------------
def test_players_requires_key(client):
    assert client.get("/players").status_code == 401


def test_players_rejects_wrong_key(client):
    resp = client.get("/players", headers={"X-API-Key": "not-the-key"})
    assert resp.status_code == 401


def test_standings_requires_key(client):
    assert client.get("/standings?tournament_id=1").status_code == 401


# ----------------------------------------------------------------------
# /players
# ----------------------------------------------------------------------
def test_players_returns_six(client, auth):
    resp = client.get("/players", headers=auth)
    assert resp.status_code == 200
    players = resp.json()
    assert len(players) == 6


def test_players_sorted_by_elo_desc(client, auth):
    players = client.get("/players", headers=auth).json()
    elos = [p["current_elo"] for p in players]
    assert elos == sorted(elos, reverse=True)
    # Carlsen is top seed in the seed data
    assert players[0]["name"] == "Magnus Carlsen"


# ----------------------------------------------------------------------
# /tournaments
# ----------------------------------------------------------------------
def test_tournaments_present(client, auth):
    resp = client.get("/tournaments", headers=auth)
    assert resp.status_code == 200
    tournaments = resp.json()
    assert len(tournaments) >= 1
    names = [t["name"] for t in tournaments]
    assert "August Invitational 2026" in names


# ----------------------------------------------------------------------
# /rating-history
# ----------------------------------------------------------------------
def test_rating_history_full(client, auth):
    resp = client.get("/rating-history", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 18  # 6 players x 3 snapshots


def test_rating_history_filtered(client, auth):
    resp = client.get("/rating-history?player_id=1", headers=auth)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 3
    assert all(r["player_id"] == 1 for r in rows)
    # newest first
    dates = [r["valid_from"] for r in rows]
    assert dates == sorted(dates, reverse=True)


# ----------------------------------------------------------------------
# /standings
# ----------------------------------------------------------------------
def test_standings_ranked_and_balanced(client, auth):
    resp = client.get("/standings?tournament_id=1", headers=auth)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 6

    # Points must be sorted descending (the ranking)
    points = [r["points"] for r in rows]
    assert points == sorted(points, reverse=True)

    # Every game distributes exactly 1 point; 6 games => 6.0 total points
    assert sum(points) == 6.0

    # Winner is Carlsen with a perfect 2/2 in the seed data
    top = rows[0]
    assert top["player_name"] == "Magnus Carlsen"
    assert top["points"] == 2.0
    assert top["wins"] == 2

    # Every player's W/D/L sums to their games_played
    for r in rows:
        assert r["wins"] + r["draws"] + r["losses"] == r["games_played"]

# ----------------------------------------------------------------------
# /buchholz invariant: sum of Buchholz == sum over players of (total_points * games_played)
# ----------------------------------------------------------------------
def test_standings_buchholz_invariant(client, auth):
    rows = client.get("/standings?tournament_id=1", headers=auth).json()
    # Every player has a buchholz field
    assert all("buchholz" in r for r in rows)
    # Invariant: sum of Buchholz == sum over players of (total_points * games_played),
    # since each player's total is added to each opponent's Buchholz once per game.
    total_buchholz = sum(r["buchholz"] for r in rows)
    expected = sum(r["points"] * r["games_played"] for r in rows)
    assert total_buchholz == expected