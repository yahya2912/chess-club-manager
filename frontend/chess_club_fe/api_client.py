"""Thin client for the Chess Club Manager API (stdlib urllib only)."""
import json
import os
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = os.environ.get("CHESS_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("CHESS_API_KEY", "dev-key-change-in-production")


class ApiError(Exception):
    def __init__(self, status, detail):
        self.status = status
        self.detail = detail
        super().__init__(f"HTTP {status}: {detail}")


def _request(method, path, params=None, body=None):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None
    headers = {"X-API-Key": API_KEY}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
            detail = payload.get("detail", str(payload))
        except Exception:
            detail = e.reason
        raise ApiError(e.code, detail)
    except urllib.error.URLError as e:
        raise ApiError(0, f"Cannot reach API at {BASE_URL} ({e.reason})")


def get_players():
    return _request("GET", "/players")


def get_tournaments():
    return _request("GET", "/tournaments")


def get_rating_history(player_id=None):
    params = {"player_id": player_id} if player_id is not None else None
    return _request("GET", "/rating-history", params=params)


def get_standings(tournament_id):
    return _request("GET", "/standings", params={"tournament_id": tournament_id})


def create_registration(player_id, tournament_id, seed=None):
    body = {"player_id": player_id, "tournament_id": tournament_id}
    if seed is not None:
        body["seed"] = seed
    return _request("POST", "/registrations", body=body)


def create_game(round_id, white_id, black_id, eco_code, result):
    return _request("POST", "/games", body={
        "round_id": round_id, "white_id": white_id, "black_id": black_id,
        "eco_code": eco_code, "result": result,
    })
