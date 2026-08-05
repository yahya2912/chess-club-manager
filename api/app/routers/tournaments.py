from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.db import fetch_all

router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    dependencies=[Depends(require_api_key)],
)


@router.get("")
def list_tournaments():
    """Return all tournaments, soonest start date first."""
    return fetch_all(
        """
        SELECT id, name, start_date, num_rounds, status
        FROM tournament
        ORDER BY start_date ASC, name ASC
        """
    )
