from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row

from app.auth import require_api_key
from app.db import get_connection
from app.elo import new_ratings

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[Depends(require_api_key)],
)

VALID_RESULTS = {"1-0", "0-1", "1/2-1/2"}


class GameIn(BaseModel):
    round_id: int
    white_id: int
    black_id: int
    eco_code: str
    result: str


@router.post("", status_code=status.HTTP_201_CREATED)
def create_game(game: GameIn):
    """Record a game and update both players' Elo (K=20), transactionally."""
    if game.white_id == game.black_id:
        raise HTTPException(status_code=400,
                            detail="white_id and black_id must differ")
    if game.result not in VALID_RESULTS:
        raise HTTPException(status_code=400,
                            detail=f"result must be one of {sorted(VALID_RESULTS)}")

    try:
        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT tournament_id FROM round WHERE id = %s",
                            (game.round_id,))
                round_row = cur.fetchone()
                if round_row is None:
                    raise HTTPException(status_code=400, detail="Unknown round_id")
                tournament_id = round_row["tournament_id"]

                cur.execute(
                    """
                    SELECT player_id FROM registration
                    WHERE tournament_id = %s AND player_id IN (%s, %s)
                    """,
                    (tournament_id, game.white_id, game.black_id),
                )
                registered = {r["player_id"] for r in cur.fetchall()}
                missing = {game.white_id, game.black_id} - registered
                if missing:
                    raise HTTPException(
                        status_code=409,
                        detail=f"player(s) not registered in tournament: {sorted(missing)}",
                    )

                cur.execute("SELECT id, current_elo FROM player WHERE id IN (%s, %s)",
                            (game.white_id, game.black_id))
                elos = {r["id"]: r["current_elo"] for r in cur.fetchall()}
                white_elo = elos[game.white_id]
                black_elo = elos[game.black_id]

                new_white, new_black = new_ratings(white_elo, black_elo, game.result)

                cur.execute(
                    """
                    INSERT INTO game (round_id, white_id, black_id, eco_code, result)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """,
                    (game.round_id, game.white_id, game.black_id,
                     game.eco_code, game.result),
                )
                game_id = cur.fetchone()["id"]

                cur.execute("UPDATE player SET current_elo = %s WHERE id = %s",
                            (new_white, game.white_id))
                cur.execute("UPDATE player SET current_elo = %s WHERE id = %s",
                            (new_black, game.black_id))
                cur.execute("INSERT INTO rating_history (player_id, elo) VALUES (%s, %s)",
                            (game.white_id, new_white))
                cur.execute("INSERT INTO rating_history (player_id, elo) VALUES (%s, %s)",
                            (game.black_id, new_black))
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400,
                            detail="Unknown round_id, player id, or eco_code")
    except psycopg.errors.CheckViolation:
        raise HTTPException(status_code=400,
                            detail="Game violates a database constraint")

    return {
        "id": game_id,
        "round_id": game.round_id,
        "white_id": game.white_id,
        "black_id": game.black_id,
        "eco_code": game.eco_code,
        "result": game.result,
        "elo_changes": {
            "white": {"before": white_elo, "after": new_white},
            "black": {"before": black_elo, "after": new_black},
        },
    }
