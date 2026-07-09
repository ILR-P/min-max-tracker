from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class SetLogInput(BaseModel):
    set_number: int = Field(ge=1, le=4)
    load: float = Field(ge=0)
    reps: int = Field(ge=0)


class WorkingSetTemplateInput(BaseModel):
    set_number: int = Field(ge=1, le=4)
    load: float = Field(ge=0)
    reps: int = Field(ge=0)
    rest_seconds: int = Field(ge=0)
    notes: str | None = None


class WorkoutQuery(BaseModel):
    user_id: str | None = None
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
    rest_seconds: int | None = None
    notes: str | None = None
    previous_week: ExercisePerformance | None = None


class ExerciseTemplateInput(BaseModel):
    exercise_name: str
    warm_up_sets: int = Field(ge=0)
    working_sets: int = Field(ge=1, le=4)
    rep_range: str
    rir_target: str | None = None
    intensity_technique: str | None = None
    rest_seconds: int = Field(ge=0, default=60)
    notes: str | None = None
    working_set_templates: list[WorkingSetTemplateInput] = Field(default_factory=list)


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
    user_id: str | None = None
    logs: list[SetLogInput]


class WorkoutLogsResponse(BaseModel):
    workout_id: str
    inserted_rows: int
    payload: list[dict[str, Any]]


class CreateWorkoutRequest(BaseModel):
    block_name: str
    block_description: str | None = None
    week_number: int = Field(ge=1, le=12)
    workout_name: str
    day_of_week: int = Field(ge=1, le=7)
    workout_summary: str | None = None
    exercises: list[ExerciseTemplateInput] = Field(default_factory=list)


class CreateWorkoutResponse(BaseModel):
    block_id: str
    week_id: str
    workout_id: str
    exercise_template_ids: list[str] = Field(default_factory=list)
