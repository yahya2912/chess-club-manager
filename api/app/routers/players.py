from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.db import fetch_all

router = APIRouter(
    prefix="/players",
    tags=["players"],
    dependencies=[Depends(require_api_key)],
)


@router.get("")
def list_players():
    """Return all players ordered by current Elo (highest first)."""
    return fetch_all(
        """
        SELECT id, name, birth_year, current_elo
        FROM player
        ORDER BY current_elo DESC, name ASC
        """
    )
