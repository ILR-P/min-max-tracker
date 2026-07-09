export const demoWorkout = {
  user_id: "demo-user",
  block_name: "Block 1 - Base Strength",
  week_number: 2,
  workout_name: "Upper 1",
  day_of_week: 2,
  workout_id: "demo-workout-upper-1",
  workout_summary:
    "Low-volume upper body work with a repeatable target and a clear previous-week reference for every exercise.",
  exercises: [
    {
      id: "demo-bench-week2",
      exercise_name: "Barbell Bench Press",
      warm_up_sets: 3,
      working_sets: 2,
      rep_range: "4-6",
      rir_target: "2",
      intensity_technique: "Top set + back-off",
      notes:
        "Keep the second set identical unless the first set misses the rep floor.",
      previous_week: {
        exercise_template_id: "demo-bench-week1",
        exercise_name: "Barbell Bench Press",
        previous_workout_name: "Upper 1",
        previous_week_sets: [
          { set_number: 1, load: 185, reps: 5, logged_date: "2026-07-02" },
          { set_number: 2, load: 185, reps: 5, logged_date: "2026-07-02" },
        ],
      },
    },
    {
      id: "demo-row-week2",
      exercise_name: "Chest-Supported Row",
      warm_up_sets: 2,
      working_sets: 2,
      rep_range: "6-8",
      rir_target: "2-3",
      intensity_technique: null,
      notes: "Pause one count at the top.",
      previous_week: {
        exercise_template_id: "demo-row-week1",
        exercise_name: "Chest-Supported Row",
        previous_workout_name: "Upper 1",
        previous_week_sets: [
          { set_number: 1, load: 140, reps: 8, logged_date: "2026-07-02" },
          { set_number: 2, load: 140, reps: 7, logged_date: "2026-07-02" },
        ],
      },
    },
    {
      id: "demo-press-week2",
      exercise_name: "Dumbbell Shoulder Press",
      warm_up_sets: 2,
      working_sets: 2,
      rep_range: "6-8",
      rir_target: "2",
      intensity_technique: null,
      notes: "Hold the same load if both sets stay in range.",
      previous_week: {
        exercise_template_id: "demo-press-week1",
        exercise_name: "Dumbbell Shoulder Press",
        previous_workout_name: "Upper 1",
        previous_week_sets: [
          { set_number: 1, load: 60, reps: 8, logged_date: "2026-07-02" },
          { set_number: 2, load: 60, reps: 8, logged_date: "2026-07-02" },
        ],
      },
    },
  ],
};
