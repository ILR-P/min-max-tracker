from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, status

from .auth import resolve_user_id
from .config import get_settings
from .database import get_supabase_client
from .schemas import WorkoutLogsRequest, WorkoutLogsResponse, WorkoutQuery, WorkoutResponse
from .service import WorkoutService

settings = get_settings()

app = FastAPI(title="Min Max Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_service() -> WorkoutService:
    return WorkoutService(get_supabase_client())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{settings['api_prefix']}/workouts/current", response_model=WorkoutResponse)
def get_current_workout(
    week_number: int,
    day_of_week: int,
    user_id: str | None = Depends(resolve_user_id),
) -> dict:
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provide a Bearer token or a user_id query parameter",
        )

    query = WorkoutQuery(user_id=user_id, week_number=week_number, day_of_week=day_of_week)
    return get_service().get_current_workout(
        user_id=query.user_id,
        week_number=query.week_number,
        day_of_week=query.day_of_week,
    )


@app.post(f"{settings['api_prefix']}/workouts/{{workout_id}}/logs", response_model=WorkoutLogsResponse)
def submit_workout_logs(
    workout_id: str,
    payload: WorkoutLogsRequest,
    user_id: str | None = Depends(resolve_user_id),
) -> dict:
    resolved_user_id = user_id or payload.user_id
    if not resolved_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provide a Bearer token or include user_id in the request body",
        )

    return get_service().submit_workout_logs(
        workout_id=workout_id,
        user_id=resolved_user_id,
        logs=[log.model_dump() for log in payload.logs],
    )
