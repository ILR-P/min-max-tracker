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

        workout = self._fetch_current_workout(user_id=user_id, week_number=week_number, day_of_week=day_of_week)
        if workout is None:
            raise HTTPException(status_code=404, detail="Workout not found")

        exercises = self._fetch_exercises(workout["id"])
        previous_workout = self._fetch_previous_workout(
            block_id=workout["block_id"],
            week_number=week_number,
            day_of_week=day_of_week,
            workout_name=workout["workout_name"],
        )
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
                self._attach_previous_week_logs(
                    user_id,
                    dict(exercise),
                    previous_by_name.get(exercise["exercise_name"].lower()),
                )
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

    def create_workout(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.client is None:
            return {
                "block_id": str(uuid4()),
                "week_id": str(uuid4()),
                "workout_id": str(uuid4()),
                "exercise_template_ids": [str(uuid4()) for _ in payload.get("exercises", [])],
            }

        block_id = self._upsert_block(user_id, payload["block_name"], payload.get("block_description"))
        week_id = self._upsert_week(block_id, payload["week_number"])
        workout_id = self._upsert_workout(week_id, payload["workout_name"], payload["day_of_week"], payload.get("workout_summary"))

        exercise_template_ids: list[str] = []
        for exercise in payload.get("exercises", []):
            exercise_template_id = self._upsert_exercise_template(workout_id, exercise)
            exercise_template_ids.append(exercise_template_id)
            self._replace_working_set_templates(exercise_template_id, exercise.get("working_set_templates", []))

        return {
            "block_id": block_id,
            "week_id": week_id,
            "workout_id": workout_id,
            "exercise_template_ids": exercise_template_ids,
        }

    def _fetch_current_workout(self, user_id: str, week_number: int, day_of_week: int) -> dict[str, Any] | None:
        week_response = (
            self.client.table("weeks")
            .select("id, block_id, week_number, blocks!inner(id, name, owner_user_id)")
            .eq("week_number", week_number)
            .eq("blocks.owner_user_id", user_id)
            .limit(1)
            .execute()
        )

        if not week_response.data:
            week_response = (
                self.client.table("weeks")
                .select("id, block_id, week_number, blocks!inner(id, name, owner_user_id)")
                .eq("week_number", week_number)
                .is_("blocks.owner_user_id", None)
                .limit(1)
                .execute()
            )

        if not week_response.data:
            return None

        week_row = week_response.data[0]
        block_row = week_row.get("blocks") or {}

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
            "block_id": week_row["block_id"],
            "block_name": block_row.get("name"),
        }

    def _fetch_previous_workout(
        self,
        block_id: str,
        week_number: int,
        day_of_week: int,
        workout_name: str,
    ) -> dict[str, Any] | None:
        previous_week_response = (
            self.client.table("weeks")
            .select("id, week_number")
            .eq("block_id", block_id)
            .lt("week_number", week_number)
            .order("week_number", desc=True)
            .limit(1)
            .execute()
        )

        if previous_week_response.data:
            previous_week_row = previous_week_response.data[0]
        else:
            wrapped_week_response = (
                self.client.table("weeks")
                .select("id, week_number")
                .eq("block_id", block_id)
                .order("week_number", desc=True)
                .limit(1)
                .execute()
            )
            if not wrapped_week_response.data:
                return None
            previous_week_row = wrapped_week_response.data[0]

        response = (
            self.client.table("workouts")
            .select("id, name, day_of_week")
            .eq("week_id", previous_week_row["id"])
            .eq("day_of_week", day_of_week)
            .eq("name", workout_name)
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
            .select("id, exercise_name, warm_up_sets, working_sets, rep_range, rir_target, intensity_technique, rest_seconds, notes")
            .eq("workout_id", workout_id)
            .order("id")
            .execute()
        )
        return list(response.data or [])

    def _upsert_block(self, user_id: str, block_name: str, block_description: str | None) -> str:
        existing = (
            self.client.table("blocks")
            .select("id")
            .eq("owner_user_id", user_id)
            .eq("name", block_name)
            .limit(1)
            .execute()
        )
        if existing.data:
            block_id = existing.data[0]["id"]
            self.client.table("blocks").update({"description": block_description}).eq("id", block_id).execute()
            return block_id

        response = self.client.table("blocks").insert({"owner_user_id": user_id, "name": block_name, "description": block_description}).execute()
        return response.data[0]["id"]

    def _upsert_week(self, block_id: str, week_number: int) -> str:
        existing = self.client.table("weeks").select("id").eq("block_id", block_id).eq("week_number", week_number).limit(1).execute()
        if existing.data:
            return existing.data[0]["id"]

        response = self.client.table("weeks").insert({"block_id": block_id, "week_number": week_number}).execute()
        return response.data[0]["id"]

    def _upsert_workout(self, week_id: str, workout_name: str, day_of_week: int, workout_summary: str | None) -> str:
        existing = (
            self.client.table("workouts")
            .select("id")
            .eq("week_id", week_id)
            .eq("day_of_week", day_of_week)
            .eq("name", workout_name)
            .limit(1)
            .execute()
        )
        if existing.data:
            workout_id = existing.data[0]["id"]
            self.client.table("workouts").update({"workout_summary": workout_summary}).eq("id", workout_id).execute()
            return workout_id

        response = self.client.table("workouts").insert({"week_id": week_id, "name": workout_name, "day_of_week": day_of_week, "workout_summary": workout_summary}).execute()
        return response.data[0]["id"]

    def _upsert_exercise_template(self, workout_id: str, exercise: dict[str, Any]) -> str:
        existing = (
            self.client.table("exercises_template")
            .select("id")
            .eq("workout_id", workout_id)
            .eq("exercise_name", exercise["exercise_name"])
            .limit(1)
            .execute()
        )
        template_payload = {
            "workout_id": workout_id,
            "exercise_name": exercise["exercise_name"],
            "warm_up_sets": exercise.get("warm_up_sets", 0),
            "working_sets": exercise.get("working_sets", 1),
            "rep_range": exercise["rep_range"],
            "rir_target": exercise.get("rir_target"),
            "intensity_technique": exercise.get("intensity_technique"),
            "rest_seconds": exercise.get("rest_seconds", 60),
            "notes": exercise.get("notes"),
        }

        if existing.data:
            template_id = existing.data[0]["id"]
            self.client.table("exercises_template").update(template_payload).eq("id", template_id).execute()
            return template_id

        response = self.client.table("exercises_template").insert(template_payload).execute()
        return response.data[0]["id"]

    def _replace_working_set_templates(self, exercise_template_id: str, working_set_templates: list[dict[str, Any]]) -> None:
        self.client.table("exercise_working_sets").delete().eq("exercise_template_id", exercise_template_id).execute()
        if not working_set_templates:
            return

        payload = [
            {
                "exercise_template_id": exercise_template_id,
                "set_number": item["set_number"],
                "load": item["load"],
                "reps": item["reps"],
                "rest_seconds": item.get("rest_seconds", 60),
                "notes": item.get("notes"),
            }
            for item in working_set_templates
        ]
        self.client.table("exercise_working_sets").insert(payload).execute()

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
        latest_log_response = (
            self.client.table("user_logs")
            .select("logged_date")
            .eq("user_id", user_id)
            .eq("exercise_template_id", exercise_template_id)
            .order("logged_date", desc=True)
            .limit(1)
            .execute()
        )

        if not latest_log_response.data:
            return []

        latest_logged_date = latest_log_response.data[0]["logged_date"]
        response = (
            self.client.table("user_logs")
            .select("set_number, load, reps, logged_date")
            .eq("user_id", user_id)
            .eq("exercise_template_id", exercise_template_id)
            .eq("logged_date", latest_logged_date)
            .order("set_number", desc=False)
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
