import { useEffect, useMemo, useState } from 'react'

import { demoWorkout } from '../data/demoWorkout'
import { getCurrentWorkout, submitWorkoutLogs } from '../lib/api'
import ExerciseCard from './ExerciseCard'
import WorkoutHeader from './WorkoutHeader'

const currentUserId = 'demo-user'
const defaultWeekNumber = 2
const defaultDayOfWeek = 2

function buildInitialSetState(exercises) {
  return exercises.reduce((accumulator, exercise) => {
    accumulator[exercise.id] = Array.from({ length: exercise.working_sets }, (_, index) => ({
      set_number: index + 1,
      load: '',
      reps: '',
    }))
    return accumulator
  }, {})
}

export default function WorkoutDashboard() {
  const [workout, setWorkout] = useState(demoWorkout)
  const [setState, setSetState] = useState(() => buildInitialSetState(demoWorkout.exercises))
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadWorkout() {
      try {
        const response = await getCurrentWorkout({
          userId: currentUserId,
          weekNumber: defaultWeekNumber,
          dayOfWeek: defaultDayOfWeek,
        })

        if (!active) {
          return
        }

        setWorkout(response)
        setSetState(buildInitialSetState(response.exercises))
        setError('')
      } catch {
        if (!active) {
          return
        }

        setWorkout(demoWorkout)
        setSetState(buildInitialSetState(demoWorkout.exercises))
        setError('Using local demo data until the API is available.')
      }
    }

    loadWorkout()

    return () => {
      active = false
    }
  }, [])

  const exerciseCount = useMemo(() => workout.exercises.length, [workout.exercises.length])

  function updateSet(exerciseId, setNumber, nextValue) {
    setSetState((currentState) => ({
      ...currentState,
      [exerciseId]: currentState[exerciseId].map((setRow) =>
        setRow.set_number === setNumber ? { ...setRow, ...nextValue } : setRow,
      ),
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setStatus('saving')
    setError('')

    const logs = workout.exercises.flatMap((exercise) =>
      (setState[exercise.id] ?? [])
        .filter((entry) => entry.load !== '' && entry.reps !== '')
        .map((entry) => ({
          exercise_template_id: exercise.id,
          set_number: entry.set_number,
          load: Number(entry.load),
          reps: Number(entry.reps),
          logged_date: new Date().toISOString().slice(0, 10),
        })),
    )

    try {
      await submitWorkoutLogs({
        workoutId: workout.workout_id,
        userId: workout.user_id ?? currentUserId,
        logs,
      })
      setStatus('saved')
    } catch {
      setStatus('idle')
      setError('Could not save logs yet. Keep using the form when the API is online.')
    }
  }

  return (
    <main className="app-shell">
      <div className="ambient ambient-left" />
      <div className="ambient ambient-right" />

      <WorkoutHeader workout={workout} />

      <section className="dashboard-strip">
        <div className="dashboard-stat">
          <span className="section-label">Program block</span>
          <strong>{workout.block_name}</strong>
        </div>
        <div className="dashboard-stat">
          <span className="section-label">Workout day</span>
          <strong>Day {workout.day_of_week}</strong>
        </div>
        <div className="dashboard-stat">
          <span className="section-label">Exercises</span>
          <strong>{exerciseCount}</strong>
        </div>
      </section>

      <form className="workout-form" onSubmit={handleSubmit}>
        {workout.exercises.map((exercise) => (
          <ExerciseCard
            key={exercise.id}
            exercise={exercise}
            setValues={setState[exercise.id] ?? []}
            onSetChange={(setNumber, nextValue) => updateSet(exercise.id, setNumber, nextValue)}
          />
        ))}

        <footer className="workout-footer">
          <div>
            <span className="section-label">Status</span>
            <strong>
              {status === 'saving'
                ? 'Saving logs'
                : status === 'saved'
                  ? 'Saved'
                  : 'Ready'}
            </strong>
          </div>
          {error ? (
            <p className="error-message">{error}</p>
          ) : (
            <p>Reference the previous week, then log your working sets.</p>
          )}
          <button type="submit">Save working sets</button>
        </footer>
      </form>
    </main>
  )
}
