function formatDateTime(value) {
  if (!value) return "—";
  return value.replace("T", " ").replace("Z", "");
}

function formatText(value) {
  if (!value) return "—";
  return value;
}

function statusClass(status) {
  if (!status) return "status-pill";
  return `status-pill status-${status.toLowerCase()}`;
}

function hasCalendarSource(meeting) {
  return (meeting.sources || []).includes("calendar");
}

export default function MeetingList({
  meetings,
  loading,
  onShowConflicts,
  onShowCalendar,
}) {
  if (loading) {
    return <p className="status-text">Loading meetings…</p>;
  }

  if (meetings.length === 0) {
    return <p className="status-text">No meetings found.</p>;
  }

  return (
    <div className="table-wrap">
      <table className="meetings-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Client</th>
            <th>Representative</th>
            <th>Type</th>
            <th>Location</th>
            <th>When</th>
            <th>Source</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {meetings.map((meeting) => {
            const showCalendar = hasCalendarSource(meeting);
            const showConflicts = meeting.has_conflict;

            return (
              <tr key={meeting.id}>
                <td>{meeting.title}</td>
                <td>
                  {meeting.client_name || "—"}
                  {meeting.client_company ? (
                    <div className="muted">{meeting.client_company}</div>
                  ) : null}
                </td>
                <td>
                  {formatText(meeting.relationship_owner || meeting.organizer)}
                </td>
                <td>{formatText(meeting.meeting_type)}</td>
                <td>{formatText(meeting.location)}</td>
                <td>{formatDateTime(meeting.start_time)}</td>
                <td>
                  <div className="source-list">
                    {(meeting.sources || []).length === 0 ? (
                      "—"
                    ) : (
                      meeting.sources.map((source) => (
                        <span
                          key={source}
                          className={`source-pill source-${source}`}
                        >
                          {source === "crm" ? "CRM" : "Calendar"}
                        </span>
                      ))
                    )}
                  </div>
                </td>
                <td>
                  {meeting.status ? (
                    <span className={statusClass(meeting.status)}>
                      {meeting.status}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td>
                  {showCalendar || showConflicts ? (
                    <div className="row-actions">
                      {showCalendar ? (
                        <button
                          type="button"
                          className="btn-calendar"
                          onClick={() => onShowCalendar(meeting)}
                        >
                          View calendar
                        </button>
                      ) : null}
                      {showConflicts ? (
                        <button
                          type="button"
                          className="btn-conflicts"
                          onClick={() => onShowConflicts(meeting)}
                        >
                          View conflicts
                        </button>
                      ) : null}
                    </div>
                  ) : (
                    <span className="muted">—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
