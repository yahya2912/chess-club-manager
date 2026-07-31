# Design Decisions

## D1 — PostgreSQL 16 as the database engine
Chosen for mature CHECK/UNIQUE/FK constraint support, which is central to this
project's approach of enforcing acceptance criteria at the DDL level rather
than only in application code.

## D2 — FastAPI as the API framework
Chosen for automatic request validation, built-in OpenAPI docs (useful for
the video demo), and straightforward `X-API-Key` header dependency injection
for the write-endpoint protection required by the acceptance criteria.

## D3 — Python/tkinter for the frontend
Chosen because it ships with the Python standard library, requires no extra
runtime dependency, and packages cleanly into a `.deb` archive -- matching the
mandatory `.deb` submission format without needing a heavier GUI framework.

## D4 — Plain Elo rating with K-factor 20
Chosen over more complex systems (e.g. Glicko) for a fixed, well-understood
formula that is easy to test deterministically for the symmetry requirement
in the acceptance criteria (both players' ratings must move symmetrically).

## D5 — Docker Compose for orchestration
Chosen for one-command deployment on the lecture server (`docker compose up
-d`), keeping Postgres and the API isolated from the host, and reproducible
setup regardless of which machine (Linux or macOS) development happens on.

## D6 — `.deb` package as the frontend submission format
Required by the course. Does not require developing on a Linux machine -- the
package is built and tested at the end using a Docker Ubuntu/Debian
container, keeping day-to-day development on macOS fully viable.


## Acceptance Criterion → Enforcement Mapping

Recorded here (rather than as inline SQL comments) so the reasoning survives
independently of the schema file and feeds directly into the Dev-Manual's
"what to watch out for when adding a function" chapter.

| # | Acceptance criterion | Enforced by | Layer |
|---|---|---|---|
| 1 | `POST /games` with `white_id = black_id` -> HTTP 400 | `game_distinct_players` CHECK constraint | Database |
| 2 | `POST /games` with `result` not in `{'1-0','0-1','1/2-1/2'}` -> HTTP 400 | `game_result_valid` CHECK constraint | Database |
| 3 | Registering the same player twice for the same tournament -> HTTP 409 | Composite primary key on `registration(player_id, tournament_id)` | Database |
| 4 | Recording a game for a player not registered in that tournament -> HTTP 409 | No FK path exists (`game` only references `round`, not `tournament`, so this can't be a single-table constraint) -- must be checked in the API by joining `game.round_id -> round.tournament_id` against `registration` before insert | Application |
| 5 | `GET /tournaments/{id}/standings` returns correct `SUM(points)` + Buchholz tiebreak | Query logic (JOIN across `registration`, `player`, `game`, `round` + aggregation) | Application |
| 6 | Every `POST` endpoint without a valid `X-API-Key` -> HTTP 401 | FastAPI dependency checking the `X-API-Key` header | Application |

**Note for future maintenance:** if a new business rule needs enforcing, check
first whether it can be expressed as a `CHECK`, `UNIQUE`, or `NOT NULL`
constraint on a single table (cheap, always-on, can't be bypassed). Only fall
back to application-layer logic when the rule genuinely spans tables that
aren't directly related by a foreign key -- as is the case for criterion 4
above, where `game` and `tournament` are two hops apart via `round`.

Also worth noting: `round(tournament_id, round_no)` carries a UNIQUE
constraint stopping duplicate round numbers within one tournament. This isn't
one of the six numbered acceptance criteria, but it's schema-level integrity
that the same reasoning applies to.
