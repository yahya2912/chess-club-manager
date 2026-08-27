from fastapi import FastAPI

from app.routers import (
    players, tournaments, rating_history, standings,
    registrations, games,
)

app = FastAPI(title="Chess Club Tournament & Rating Manager API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(players.router)
app.include_router(tournaments.router)
app.include_router(rating_history.router)
app.include_router(standings.router)
app.include_router(registrations.router)
app.include_router(games.router)
