from datetime import date

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from psycopg.rows import dict_row

from app.auth import require_api_key
from app.db import fetch_all, get_connection

router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    dependencies=[Depends(require_api_key)],
)


class TournamentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    num_rounds: int = Field(ge=1, le=50)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value


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


@router.post("", status_code=status.HTTP_201_CREATED)
def create_tournament(tournament: TournamentCreate):
    """Create a planned tournament and all of its rounds atomically."""
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO tournament (name, start_date, num_rounds, status)
                VALUES (%s, %s, %s, 'planned')
                RETURNING id, name, start_date, num_rounds, status
                """,
                (
                    tournament.name,
                    tournament.start_date,
                    tournament.num_rounds,
                ),
            )

            created = cur.fetchone()
            rounds = []

            for round_no in range(1, tournament.num_rounds + 1):
                cur.execute(
                    """
                    INSERT INTO round (tournament_id, round_no)
                    VALUES (%s, %s)
                    RETURNING id, round_no
                    """,
                    (created["id"], round_no),
                )
                rounds.append(cur.fetchone())

            return {**created, "rounds": rounds}
