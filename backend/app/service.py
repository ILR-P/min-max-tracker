from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

DEMO_PROGRAM: dict[str, Any] = {
    "block_name": "Block 1 - Base Strength",
    "week_number": 2,
    "workout_id": "demo-workout-upper-1",
    "workout_name": "Upper 1",
    "day_of_week": 2,
    "workout_summary": "Low-volume upper body work with a repeatable target and a clear previous-week reference for every exercise.",
    "exercises": [
        {
            "id": "demo-bench-week2",
            "exercise_name": "Barbell Bench Press",
            "warm_up_sets": 3,
            "working_sets": 2,
            "rep_range": "4-6",
            "rir_target": "2",
            "intensity_technique": "Top set + back-off",
            "notes": "Keep the second set identical unless the first set misses the rep floor.",
            "previous_week": {
                "exercise_template_id": "demo-bench-week1",
                "exercise_name": "Barbell Bench Press",
                "previous_workout_name": "Upper 1",
                "previous_week_sets": [
                    {"set_number": 1, "load": 185, "reps": 5, "logged_date": date(2026, 7, 2)},
                    {"set_number": 2, "load": 185, "reps": 5, "logged_date": date(2026, 7, 2)},
                ],
            },
        },
        {
            "id": "demo-row-week2",
            "exercise_name": "Chest-Supported Row",
            "warm_up_sets": 2,
            "working_sets": 2,
            "rep_range": "6-8",
            "rir_target": "2-3",
            "intensity_technique": None,
            "notes": "Pause one count at the top.",
            "previous_week": {
                "exercise_template_id": "demo-row-week1",
                "exercise_name": "Chest-Supported Row",
                "previous_workout_name": "Upper 1",
                "previous_week_sets": [
                    {"set_number": 1, "load": 140, "reps": 8, "logged_date": date(2026, 7, 2)},
                    {"set_number": 2, "load": 140, "reps": 7, "logged_date": date(2026, 7, 2)},
                ],
            },
        },
        {
            "id": "demo-press-week2",
            "exercise_name": "Dumbbell Shoulder Press",
            "warm_up_sets": 2,
            "working_sets": 2,
            "rep_range": "6-8",
            "rir_target": "2",
            "intensity_technique": None,
            "notes": "Hold the same load if both sets stay in range.",
            "previous_week": {
                "exercise_template_id": "demo-press-week1",
                "exercise_name": "Dumbbell Shoulder Press",
                "previous_workout_name": "Upper 1",
                "previous_week_sets": [
                    {"set_number": 1, "load": 60, "reps": 8, "logged_date": date(2026, 7, 2)},
                    {"set_number": 2, "load": 60, "reps": 8, "logged_date": date(2026, 7, 2)},
                ],
            },
        },
    ],
}


class WorkoutService:
    def __init__(self, client: Any | None) -> None:
        self.client = client

    def get_current_workout(self, user_id: str, week_number: int, day_of_week: int) -> dict[str, Any]:
        if self.client is None:
            return self._demo_workout(user_id=user_id, week_number=week_number, day_of_week=day_of_week)

        workout = self._fetch_current_workout(week_number=week_number, day_of_week=day_of_week)
        if workout is None:
            raise HTTPException(status_code=404, detail="Workout not found")

        exercises = self._fetch_exercises(workout["id"])
        previous_workout = self._fetch_previous_workout(week_number=week_number, day_of_week=day_of_week)
        previous_exercises = self._fetch_exercises(previous_workout["id"]) if previous_workout else []
        previous_by_name = {exercise["exercise_name"].lower(): exercise for exercise in previous_exercises}

        return {
            "user_id": user_id,
            "block_name": workout["block_name"],
            "week_number": week_number,
            "workout_id": workout["id"],
            "workout_name": workout["workout_name"],
            "day_of_week": day_of_week,
            "workout_summary": workout.get("workout_summary"),
            "exercises": [
                self._attach_previous_week_logs(user_id, dict(exercise), previous_by_name.get(exercise["exercise_name"].lower()))
                for exercise in exercises
            ],
        }

    def submit_workout_logs(self, workout_id: str, user_id: str, logs: list[dict[str, Any]]) -> dict[str, Any]:
        if self.client is None:
            return {
                "workout_id": workout_id,
                "inserted_rows": len(logs),
                "payload": [
                    {
                        "id": str(uuid4()),
                        "user_id": user_id,
                        "workout_id": workout_id,
                        **log,
                    }
                    for log in logs
                ],
            }

        payload = [{"user_id": user_id, "workout_id": workout_id, **log} for log in logs]
        result = self.client.table("user_logs").insert(payload).execute()

        return {"workout_id": workout_id, "inserted_rows": len(result.data or payload), "payload": result.data or payload}

    def _fetch_current_workout(self, week_number: int, day_of_week: int) -> dict[str, Any] | None:
        week_response = (
            self.client.table("weeks")
            .select("id, block_id, week_number")
            .eq("week_number", week_number)
            .limit(1)
            .execute()
        )

        if not week_response.data:
            return None

        week_row = week_response.data[0]
        block_response = (
            self.client.table("blocks")
            .select("id, name")
            .eq("id", week_row["block_id"])
            .limit(1)
            .execute()
        )
        block_row = block_response.data[0] if block_response.data else {}

        workout_response = (
            self.client.table("workouts")
            .select("id, name, day_of_week, workout_summary")
            .eq("week_id", week_row["id"])
            .eq("day_of_week", day_of_week)
            .limit(1)
            .execute()
        )

        if not workout_response.data:
            return None

        workout_row = workout_response.data[0]
        return {
            "id": workout_row["id"],
            "workout_name": workout_row["name"],
            "day_of_week": workout_row["day_of_week"],
            "workout_summary": workout_row.get("workout_summary"),
            "week_number": week_row.get("week_number"),
            "block_name": block_row.get("name"),
        }

    def _fetch_previous_workout(self, week_number: int, day_of_week: int) -> dict[str, Any] | None:
        if week_number <= 1:
            return None

        week_response = (
            self.client.table("weeks")
            .select("id, week_number")
            .eq("week_number", week_number - 1)
            .limit(1)
            .execute()
        )

        if not week_response.data:
            return None

        previous_week_row = week_response.data[0]
        response = (
            self.client.table("workouts")
            .select("id, name, day_of_week")
            .eq("week_id", previous_week_row["id"])
            .eq("day_of_week", day_of_week)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]
        return {"id": row["id"], "workout_name": row["name"]}

    def _fetch_exercises(self, workout_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("exercises_template")
            .select("id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, notes")
            .eq("workout_id", workout_id)
            .order("id")
            .execute()
        )
        return list(response.data or [])

    def _attach_previous_week_logs(
        self,
        user_id: str,
        current_exercise: dict[str, Any],
        previous_exercise: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if previous_exercise is None:
            current_exercise["previous_week"] = {
                "exercise_template_id": None,
                "exercise_name": current_exercise["exercise_name"],
                "previous_workout_name": None,
                "previous_week_sets": [],
            }
            return current_exercise

        logs = self._fetch_previous_week_logs(user_id, previous_exercise["id"])
        current_exercise["previous_week"] = {
            "exercise_template_id": previous_exercise["id"],
            "exercise_name": previous_exercise["exercise_name"],
            "previous_workout_name": None,
            "previous_week_sets": logs,
        }
        return current_exercise

    def _fetch_previous_week_logs(self, user_id: str, exercise_template_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table("user_logs")
            .select("set_number, load, reps, logged_date")
            .eq("user_id", user_id)
            .eq("exercise_template_id", exercise_template_id)
            .order("logged_date", desc=True)
            .order("set_number", desc=False)
            .limit(2)
            .execute()
        )
        return list(response.data or [])

    def _demo_workout(self, user_id: str, week_number: int, day_of_week: int) -> dict[str, Any]:
        program = dict(DEMO_PROGRAM)
        program["user_id"] = user_id
        program["week_number"] = week_number
        program["day_of_week"] = day_of_week
        program["exercises"] = [dict(exercise) for exercise in DEMO_PROGRAM["exercises"]]
        return program
