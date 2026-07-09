import PreviousWeekPerformance from './PreviousWeekPerformance'
import SetEntryRow from './SetEntryRow'

export default function ExerciseCard({ exercise, setValues, onSetChange }) {
  const workingSetRows = Array.from({ length: exercise.working_sets }, (_, index) => index + 1)

  return (
    <article className="exercise-card">
      <header className="exercise-card-header">
        <div>
          <div className="section-label">Exercise</div>
          <h3>{exercise.exercise_name}</h3>
        </div>
        <div className="exercise-meta">
          <span>{exercise.warm_up_sets} warm-up sets</span>
          <span>{exercise.working_sets} working sets</span>
          <span>{exercise.rep_range} reps</span>
          {exercise.rir_target ? <span>RIR {exercise.rir_target}</span> : null}
        </div>
      </header>

      <div className="exercise-notes">
        {exercise.intensity_technique ? <span>{exercise.intensity_technique}</span> : null}
        {exercise.notes ? <p>{exercise.notes}</p> : null}
      </div>

      <PreviousWeekPerformance previousWeek={exercise.previous_week} />

      <div className="set-entry-grid">
        {workingSetRows.map((setNumber) => (
          <SetEntryRow
            key={setNumber}
            setNumber={setNumber}
            value={setValues[setNumber] ?? { load: '', reps: '' }}
            onChange={(nextValue) => onSetChange(setNumber, nextValue)}
          />
        ))}
      </div>
    </article>
  )
}
