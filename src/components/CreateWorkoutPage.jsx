import { useMemo, useState } from 'react'

import { createWorkoutTemplate } from '../lib/api'

const MAX_WORKING_SETS = 4

function createWorkingSet(setNumber) {
  return {
    set_number: setNumber,
    load: '',
    reps: '',
    rest_seconds: '',
    notes: '',
  }
}

function createExercise(index, workingSets = 2) {
  return {
    exercise_name: `Exercise ${index + 1}`,
    warm_up_sets: 2,
    working_sets: workingSets,
    rep_range: '4-6',
    rir_target: '2',
    intensity_technique: '',
    rest_seconds: 90,
    notes: '',
    working_set_templates: Array.from({ length: workingSets }, (_, setIndex) => createWorkingSet(setIndex + 1)),
  }
}

function cloneExercise(exercise) {
  return {
    ...exercise,
    working_set_templates: exercise.working_set_templates.map((setRow) => ({ ...setRow })),
  }
}

function normalizeWorkingSets(exercise) {
  const count = Number(exercise.working_sets) || 1
  return Array.from({ length: count }, (_, index) => exercise.working_set_templates[index] ?? createWorkingSet(index + 1))
}

function updateExercise(exercises, exerciseIndex, updater) {
  return exercises.map((exercise, currentIndex) => {
    if (currentIndex !== exerciseIndex) {
      return exercise
    }

    const nextExercise = updater(exercise)
    return {
      ...nextExercise,
      working_set_templates: normalizeWorkingSets(nextExercise),
    }
  })
}

export default function CreateWorkoutPage({ session }) {
  const [blockName, setBlockName] = useState('Block 1 - Base Strength')
  const [blockDescription, setBlockDescription] = useState('Weeks 1-6: accumulate crisp low-volume work with steady loading.')
  const [weekNumber, setWeekNumber] = useState(1)
  const [workoutName, setWorkoutName] = useState('Upper 1')
  const [dayOfWeek, setDayOfWeek] = useState(1)
  const [workoutSummary, setWorkoutSummary] = useState('')
  const [exercises, setExercises] = useState([createExercise(0)])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const exerciseCount = useMemo(() => exercises.length, [exercises.length])

  function duplicateToNextWeek() {
    setWeekNumber((currentWeek) => Math.min(Number(currentWeek) + 1, 12))
    setExercises((currentExercises) => currentExercises.map((exercise) => cloneExercise(exercise)))
    setSuccess('Copied this workout to the next week. Adjust the differences and save again.')
    setError('')
  }

  function setWorkingSetValue(exerciseIndex, setIndex, field, value) {
    setExercises((current) =>
      updateExercise(current, exerciseIndex, (exercise) => ({
        ...exercise,
        working_set_templates: exercise.working_set_templates.map((setRow, currentSetIndex) =>
          currentSetIndex === setIndex ? { ...setRow, [field]: value } : setRow,
        ),
      })),
    )
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const payload = {
        block_name: blockName,
        block_description: blockDescription,
        week_number: Number(weekNumber),
        workout_name: workoutName,
        day_of_week: Number(dayOfWeek),
        workout_summary: workoutSummary,
        exercises: exercises.map((exercise) => ({
          exercise_name: exercise.exercise_name,
          warm_up_sets: Number(exercise.warm_up_sets),
          working_sets: Number(exercise.working_sets),
          rep_range: exercise.rep_range,
          rir_target: exercise.rir_target || null,
          intensity_technique: exercise.intensity_technique || null,
          rest_seconds: Number(exercise.rest_seconds) || 60,
          notes: exercise.notes || null,
          working_set_templates: exercise.working_set_templates.map((setRow) => ({
            set_number: Number(setRow.set_number),
            load: Number(setRow.load) || 0,
            reps: Number(setRow.reps) || 0,
            rest_seconds: Number(setRow.rest_seconds) || Number(exercise.rest_seconds) || 60,
            notes: setRow.notes || null,
          })),
        })),
      }

      await createWorkoutTemplate({ payload, session })
      setSuccess('Workout saved to Supabase.')
    } catch (createError) {
      setError(createError.message || 'Failed to save workout')
    }

    setSaving(false)
  }

  return (
    <main className="page-shell">
      <section className="create-hero">
        <div>
          <p className="eyebrow">Create workout</p>
          <h1>Build a workout template</h1>
          <p className="workout-summary">
            Save the block, week, workout day, exercises, working sets, load, reps, rest, and notes directly to Supabase.
          </p>
        </div>
        <div className="dashboard-stat create-stat">
          <span className="section-label">Exercises</span>
          <strong>{exerciseCount}</strong>
        </div>
      </section>

      <form className="create-form" onSubmit={handleSubmit}>
        <section className="create-card create-grid">
          <label>
            Block name
            <input value={blockName} onChange={(event) => setBlockName(event.target.value)} />
          </label>
          <label>
            Block description
            <input value={blockDescription} onChange={(event) => setBlockDescription(event.target.value)} />
          </label>
          <label>
            Week number
            <input type="number" min="1" max="12" value={weekNumber} onChange={(event) => setWeekNumber(event.target.value)} />
          </label>
          <label>
            Workout name
            <input value={workoutName} onChange={(event) => setWorkoutName(event.target.value)} />
          </label>
          <label>
            Day of week
            <select value={dayOfWeek} onChange={(event) => setDayOfWeek(event.target.value)}>
              <option value={1}>Monday</option>
              <option value={2}>Tuesday</option>
              <option value={3}>Wednesday</option>
              <option value={4}>Thursday</option>
              <option value={5}>Friday</option>
            </select>
          </label>
          <label className="create-span-2">
            Workout summary
            <input value={workoutSummary} onChange={(event) => setWorkoutSummary(event.target.value)} />
          </label>
        </section>

        {exercises.map((exercise, exerciseIndex) => (
          <section key={exerciseIndex} className="create-card create-exercise-card">
            <div className="create-card-header">
              <div>
                <div className="section-label">Exercise {exerciseIndex + 1}</div>
                <h2>{exercise.exercise_name}</h2>
              </div>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setExercises((current) => current.filter((_, currentIndex) => currentIndex !== exerciseIndex))}
                disabled={exercises.length === 1}
              >
                Remove
              </button>
            </div>

            <div className="create-grid">
              <label>
                Exercise name
                <input value={exercise.exercise_name} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, exercise_name: event.target.value })))} />
              </label>
              <label>
                Warm-up sets
                <input type="number" min="0" value={exercise.warm_up_sets} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, warm_up_sets: event.target.value })))} />
              </label>
              <label>
                Working sets
                <select value={exercise.working_sets} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, working_sets: Number(event.target.value) })))}>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                  <option value={3}>3</option>
                  <option value={4}>4</option>
                </select>
              </label>
              <label>
                Rep range
                <input value={exercise.rep_range} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, rep_range: event.target.value })))} />
              </label>
              <label>
                RIR target
                <input value={exercise.rir_target} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, rir_target: event.target.value })))} />
              </label>
              <label>
                Intensity technique
                <input value={exercise.intensity_technique} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, intensity_technique: event.target.value })))} />
              </label>
              <label>
                Default rest seconds
                <input type="number" min="0" value={exercise.rest_seconds} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, rest_seconds: event.target.value })))} />
              </label>
              <label className="create-span-2">
                Exercise notes
                <input value={exercise.notes} onChange={(event) => setExercises((current) => updateExercise(current, exerciseIndex, (item) => ({ ...item, notes: event.target.value })))} />
              </label>
            </div>

            <div className="create-working-sets">
              {exercise.working_set_templates.slice(0, Number(exercise.working_sets) || 1).map((setRow, setIndex) => (
                <div key={setRow.set_number} className="create-working-set-row">
                  <div className="section-label">Set {setRow.set_number}</div>
                  <input type="number" min="0" placeholder="Load" value={setRow.load} onChange={(event) => setWorkingSetValue(exerciseIndex, setIndex, 'load', event.target.value)} />
                  <input type="number" min="0" placeholder="Reps" value={setRow.reps} onChange={(event) => setWorkingSetValue(exerciseIndex, setIndex, 'reps', event.target.value)} />
                  <input type="number" min="0" placeholder="Rest" value={setRow.rest_seconds} onChange={(event) => setWorkingSetValue(exerciseIndex, setIndex, 'rest_seconds', event.target.value)} />
                  <input className="create-span-2" placeholder="Set note" value={setRow.notes} onChange={(event) => setWorkingSetValue(exerciseIndex, setIndex, 'notes', event.target.value)} />
                </div>
              ))}
            </div>
          </section>
        ))}

        <div className="create-controls">
          <button type="button" className="ghost-button" onClick={duplicateToNextWeek}>
            Duplicate to next week
          </button>
          <button type="button" className="ghost-button" onClick={() => setExercises((current) => [...current, createExercise(current.length, 2)])}>
            Add exercise
          </button>
          <button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Create workout'}
          </button>
        </div>

        {error ? <p className="error-message">{error}</p> : null}
        {success ? <p className="auth-notice">{success}</p> : null}
      </form>
    </main>
  )
}