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
    """Tournament standings ranked by points, then Buchholz, then wins.

    Scoring: win = 1.0, draw = 0.5, loss = 0.0.
    Buchholz (full): the sum of every opponent's total tournament points.
    """
    return fetch_all(
        """
        WITH per_game AS (
            SELECT g.white_id AS player_id,
                   g.black_id AS opponent_id,
                   CASE g.result WHEN '1-0' THEN 1.0
                                 WHEN '0-1' THEN 0.0
                                 ELSE 0.5 END AS points,
                   CASE g.result WHEN '1-0' THEN 1 ELSE 0 END AS win,
                   CASE g.result WHEN '0-1' THEN 1 ELSE 0 END AS loss,
                   CASE g.result WHEN '1/2-1/2' THEN 1 ELSE 0 END AS draw
            FROM game g
            JOIN round r ON r.id = g.round_id
            WHERE r.tournament_id = %(tid)s

            UNION ALL

            SELECT g.black_id AS player_id,
                   g.white_id AS opponent_id,
                   CASE g.result WHEN '0-1' THEN 1.0
                                 WHEN '1-0' THEN 0.0
                                 ELSE 0.5 END AS points,
                   CASE g.result WHEN '0-1' THEN 1 ELSE 0 END AS win,
                   CASE g.result WHEN '1-0' THEN 1 ELSE 0 END AS loss,
                   CASE g.result WHEN '1/2-1/2' THEN 1 ELSE 0 END AS draw
            FROM game g
            JOIN round r ON r.id = g.round_id
            WHERE r.tournament_id = %(tid)s
        ),
        totals AS (
            SELECT player_id, SUM(points) AS total_points
            FROM per_game
            GROUP BY player_id
        ),
        buchholz AS (
            SELECT pg.player_id,
                   COALESCE(SUM(opp.total_points), 0) AS buchholz
            FROM per_game pg
            JOIN totals opp ON opp.player_id = pg.opponent_id
            GROUP BY pg.player_id
        )
        SELECT p.id                              AS player_id,
               p.name                            AS player_name,
               reg.seed,
               COALESCE(SUM(pg.points), 0)       AS points,
               COALESCE(SUM(pg.win), 0)          AS wins,
               COALESCE(SUM(pg.draw), 0)         AS draws,
               COALESCE(SUM(pg.loss), 0)         AS losses,
               COUNT(pg.player_id)               AS games_played,
               COALESCE(MAX(b.buchholz), 0)      AS buchholz
        FROM registration reg
        JOIN player p ON p.id = reg.player_id
        LEFT JOIN per_game pg ON pg.player_id = reg.player_id
        LEFT JOIN buchholz b ON b.player_id = reg.player_id
        WHERE reg.tournament_id = %(tid)s
        GROUP BY p.id, p.name, reg.seed
        ORDER BY points DESC, buchholz DESC, wins DESC, p.name ASC
        """,
        {"tid": tournament_id},
    )
