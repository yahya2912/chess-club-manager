
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
