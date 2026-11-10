function formatValue(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export default function ConflictModal({
  meeting,
  conflicts,
  loading,
  error,
  onClose,
}) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        onClick={(event) => {
          // Keep clicks inside the modal from closing it
          event.stopPropagation();
        }}
      >
        <div className="modal-header">
          <div>
            <h2>Conflicts</h2>
            <p className="muted">
              Meeting #{meeting.id} — {meeting.title}
            </p>
          </div>
          <button type="button" onClick={onClose}>
            Close
          </button>
        </div>

        {loading && <p className="status-text">Loading conflicts…</p>}

        {error && <p className="error-banner">{error}</p>}

        {!loading && !error && conflicts.length === 0 && (
          <p className="status-text">No conflict rows returned.</p>
        )}

        {!loading && !error && conflicts.length > 0 && (
          <div className="table-wrap">
            <table className="conflicts-table">
              <thead>
                <tr>
                  <th>Field</th>
                  <th>CRM value</th>
                  <th>Calendar value</th>
                  <th>Chosen</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {conflicts.map((conflict) => (
                  <tr key={conflict.id}>
                    <td>{conflict.field}</td>
                    <td>{formatValue(conflict.crm_value)}</td>
                    <td>{formatValue(conflict.calendar_value)}</td>
                    <td>{formatValue(conflict.chosen)}</td>
                    <td>{conflict.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
