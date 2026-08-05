from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.db import fetch_all

router = APIRouter(
    prefix="/standings",
    tags=["standings"],
    dependencies=[Depends(require_api_key)],
)


@router.get("")
def get_standings(tournament_id: int):
    """Tournament standings: points, wins, draws, losses, games played,
    per registered player, ranked by points (highest first).

    Scoring: win = 1.0, draw = 0.5, loss = 0.0.
    Players registered but with no games yet appear with zeros.
    """
    return fetch_all(
        """
        WITH results AS (
            -- Each player's outcome per game, from their own colour's view
            SELECT g.white_id AS player_id,
                   CASE g.result
                       WHEN '1-0'     THEN 1.0
                       WHEN '0-1'     THEN 0.0
                       ELSE 0.5
                   END AS points,
                   CASE g.result WHEN '1-0' THEN 1 ELSE 0 END AS win,
                   CASE g.result WHEN '0-1' THEN 1 ELSE 0 END AS loss,
                   CASE g.result WHEN '1/2-1/2' THEN 1 ELSE 0 END AS draw
            FROM game g
            JOIN round r ON r.id = g.round_id
            WHERE r.tournament_id = %(tid)s

            UNION ALL

            SELECT g.black_id AS player_id,
                   CASE g.result
                       WHEN '0-1'     THEN 1.0
                       WHEN '1-0'     THEN 0.0
                       ELSE 0.5
                   END AS points,
                   CASE g.result WHEN '0-1' THEN 1 ELSE 0 END AS win,
                   CASE g.result WHEN '1-0' THEN 1 ELSE 0 END AS loss,
                   CASE g.result WHEN '1/2-1/2' THEN 1 ELSE 0 END AS draw
            FROM game g
            JOIN round r ON r.id = g.round_id
            WHERE r.tournament_id = %(tid)s
        )
        SELECT p.id AS player_id,
               p.name AS player_name,
               reg.seed,
               COALESCE(SUM(res.points), 0)      AS points,
               COALESCE(SUM(res.win), 0)         AS wins,
               COALESCE(SUM(res.draw), 0)        AS draws,
               COALESCE(SUM(res.loss), 0)        AS losses,
               COUNT(res.player_id)              AS games_played
        FROM registration reg
        JOIN player p ON p.id = reg.player_id
        LEFT JOIN results res ON res.player_id = reg.player_id
        WHERE reg.tournament_id = %(tid)s
        GROUP BY p.id, p.name, reg.seed
        ORDER BY points DESC, wins DESC, p.name ASC
        """,
        {"tid": tournament_id},
    )
