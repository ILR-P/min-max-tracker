export default function WorkoutHeader({ workout }) {
  return (
    <header className="workout-header">
      <div>
        <p className="eyebrow">12-week low-volume program</p>
        <h1>
          Week {workout.week_number}, {workout.workout_name}
        </h1>
        <p className="workout-summary">{workout.workout_summary}</p>
      </div>

      <div className="workout-badges">
        <span>{workout.block_name}</span>
        <span>Day {workout.day_of_week}</span>
        <span>{workout.exercises.length} exercises</span>
      </div>
    </header>
  )
}
