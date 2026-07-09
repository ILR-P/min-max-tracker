export default function PreviousWeekPerformance({ previousWeek }) {
  const sets = previousWeek?.previous_week_sets ?? []

  return (
    <section className="previous-week-card">
      <div className="section-label">Previous week</div>
      {previousWeek?.previous_workout_name ? (
        <div className="previous-week-title">{previousWeek.previous_workout_name}</div>
      ) : (
        <div className="previous-week-title muted">No reference found</div>
      )}

      <div className="previous-week-sets">
        {sets.length > 0 ? (
          sets.map((set) => (
            <div key={`${set.set_number}-${set.logged_date}`} className="previous-week-set">
              <span>Set {set.set_number}</span>
              <strong>{set.load} lb</strong>
              <span>{set.reps} reps</span>
            </div>
          ))
        ) : (
          <p className="muted">Use this week to establish a new baseline.</p>
        )}
      </div>
    </section>
  )
}
