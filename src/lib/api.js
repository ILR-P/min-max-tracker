const API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

async function buildAuthHeaders(session) {
  if (!session?.access_token) {
    return {};
  }

  return {
    Authorization: `Bearer ${session.access_token}`,
  };
}

export async function getCurrentWorkout({ weekNumber, dayOfWeek, session }) {
  const url = new URL(
    `${API_BASE_URL}/api/workouts/current`,
    window.location.origin,
  );
  url.searchParams.set("week_number", String(weekNumber));
  url.searchParams.set("day_of_week", String(dayOfWeek));

  const response = await fetch(url, {
    headers: await buildAuthHeaders(session),
  });
  if (!response.ok) {
    throw new Error(`Failed to load workout: ${response.status}`);
  }

  return response.json();
}

export async function submitWorkoutLogs({ workoutId, logs, session }) {
  const response = await fetch(
    `${API_BASE_URL}/api/workouts/${workoutId}/logs`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(await buildAuthHeaders(session)),
      },
      body: JSON.stringify({ logs }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to save logs: ${response.status}`);
  }

  return response.json();
}

export async function createWorkoutTemplate({ payload, session }) {
  const response = await fetch(`${API_BASE_URL}/api/workouts/create`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await buildAuthHeaders(session)),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to create workout: ${response.status}`);
  }

  return response.json();
}
