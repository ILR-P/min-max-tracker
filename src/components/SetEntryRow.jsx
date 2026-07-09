export default function SetEntryRow({ setNumber, value, onChange }) {
  return (
    <label className="set-entry-row">
      <span className="set-index">Set {setNumber}</span>
      <input
        type="number"
        min="0"
        step="0.5"
        inputMode="decimal"
        placeholder="Load"
        value={value.load}
        onChange={(event) => onChange({ ...value, load: event.target.value })}
      />
      <input
        type="number"
        min="0"
        step="1"
        inputMode="numeric"
        placeholder="Reps"
        value={value.reps}
        onChange={(event) => onChange({ ...value, reps: event.target.value })}
      />
    </label>
  )
}
