from fastapi import FastAPI

from app.routers import players, tournaments

app = FastAPI(title="Chess Club Tournament & Rating Manager API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(players.router)
app.include_router(tournaments.router)
