from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import psycopg

from app.auth import require_api_key
from app.db import get_connection

router = APIRouter(
    prefix="/registrations",
    tags=["registrations"],
    dependencies=[Depends(require_api_key)],
)


class RegistrationIn(BaseModel):
    player_id: int
    tournament_id: int
    seed: int | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_registration(reg: RegistrationIn):
    """Register a player for a tournament. Duplicate -> 409 (composite PK)."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO registration (player_id, tournament_id, seed)
                    VALUES (%s, %s, %s)
                    """,
                    (reg.player_id, reg.tournament_id, reg.seed),
                )
    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player already registered for this tournament",
        )
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown player_id or tournament_id",
        )
    return {
        "player_id": reg.player_id,
        "tournament_id": reg.tournament_id,
        "seed": reg.seed,
    }
