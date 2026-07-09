from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class SetLogInput(BaseModel):
    set_number: int = Field(ge=1, le=2)
    load: float = Field(ge=0)
    reps: int = Field(ge=0)


class WorkoutQuery(BaseModel):
    user_id: str
    week_number: int = Field(ge=1, le=12)
    day_of_week: int = Field(ge=1, le=7)


class PreviousWeekSet(BaseModel):
    set_number: int
    load: float
    reps: int
    logged_date: date | None = None


class ExercisePerformance(BaseModel):
    exercise_template_id: str | None = None
    exercise_name: str
    previous_workout_name: str | None = None
    previous_week_sets: list[PreviousWeekSet] = Field(default_factory=list)


class ExerciseTemplate(BaseModel):
    id: str
    exercise_name: str
    warm_up_sets: int
    working_sets: int
    rep_range: str
    rir_target: str | None = None
    intensity_technique: str | None = None
    notes: str | None = None
    previous_week: ExercisePerformance | None = None


class WorkoutResponse(BaseModel):
    user_id: str
    block_name: str
    week_number: int
    workout_name: str
    day_of_week: int
    workout_id: str
    workout_summary: str | None = None
    exercises: list[ExerciseTemplate] = Field(default_factory=list)


class WorkoutLogsRequest(BaseModel):
    user_id: str
    logs: list[SetLogInput]


class WorkoutLogsResponse(BaseModel):
    workout_id: str
    inserted_rows: int
    payload: list[dict[str, Any]]
