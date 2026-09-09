from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from psycopg.rows import dict_row

from app.auth import require_api_key
from app.db import fetch_all, get_connection


router = APIRouter(
    prefix="/players",
    tags=["players"],
    dependencies=[Depends(require_api_key)],
)


class PlayerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_year: int | None = None
    current_elo: int = Field(default=1000, ge=0, le=4000)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value

    @field_validator("birth_year")
    @classmethod
    def validate_birth_year(cls, value: int | None) -> int | None:
        if value is None:
            return None

        current_year = datetime.now().year

        if value < 1900 or value > current_year:
            raise ValueError(
                f"birth_year must be between 1900 and {current_year}"
            )

        return value


@router.get("")
def list_players():
    """Return all players ordered by current Elo."""
    return fetch_all(
        """
        SELECT id, name, birth_year, current_elo
        FROM player
        ORDER BY current_elo DESC, name ASC
        """
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_player(player: PlayerCreate):
    """Create a player and initial rating-history entry."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            cur.execute(
                """
                INSERT INTO player (name, birth_year, current_elo)
                VALUES (%s, %s, %s)
                RETURNING id, name, birth_year, current_elo
                """,
                (
                    player.name,
                    player.birth_year,
                    player.current_elo,
                ),
            )

            created = cur.fetchone()

            if created is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create player",
                )

            cur.execute(
                """
                INSERT INTO rating_history (player_id, elo)
                VALUES (%s, %s)
                """,
                (
                    created["id"],
                    created["current_elo"],
                ),
            )

            return created
