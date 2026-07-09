const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export async function getCurrentWorkout({ userId, weekNumber, dayOfWeek }) {
  const url = new URL(
    `${API_BASE_URL}/api/workouts/current`,
    window.location.origin,
  );
  url.searchParams.set("user_id", userId);
  url.searchParams.set("week_number", String(weekNumber));
  url.searchParams.set("day_of_week", String(dayOfWeek));

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load workout: ${response.status}`);
  }

  return response.json();
}

export async function submitWorkoutLogs({ workoutId, userId, logs }) {
  const response = await fetch(
    `${API_BASE_URL}/api/workouts/${workoutId}/logs`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id: userId, logs }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to save logs: ${response.status}`);
  }

  return response.json();
}
