from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.db import fetch_all

router = APIRouter(
    prefix="/rating-history",
    tags=["rating-history"],
    dependencies=[Depends(require_api_key)],
)


@router.get("")
def list_rating_history(player_id: int | None = None):
    """Return Elo history, newest first.
    Optional ?player_id=N narrows to a single player.
    """
    if player_id is None:
        return fetch_all(
            """
            SELECT rh.id, rh.player_id, p.name AS player_name,
                   rh.valid_from, rh.elo
            FROM rating_history rh
            JOIN player p ON p.id = rh.player_id
            ORDER BY rh.valid_from DESC, rh.player_id ASC
            """
        )
    return fetch_all(
        """
        SELECT rh.id, rh.player_id, p.name AS player_name,
               rh.valid_from, rh.elo
        FROM rating_history rh
        JOIN player p ON p.id = rh.player_id
        WHERE rh.player_id = %s
        ORDER BY rh.valid_from DESC
        """,
        (player_id,),
    )
