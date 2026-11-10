function formatText(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

function formatDateTime(value) {
  if (!value) return "—";
  return value.replace("T", " ").replace("Z", "");
}

function formatAttendees(attendees) {
  if (!attendees || attendees.length === 0) return "—";
  return attendees.join(", ");
}

export default function CalendarModal({ meeting, onClose }) {
  const rows = [
    { label: "Event ID", value: formatText(meeting.event_id) },
    { label: "Organizer", value: formatText(meeting.organizer) },
    { label: "Attendees", value: formatAttendees(meeting.attendees) },
    { label: "Start", value: formatDateTime(meeting.start_time) },
    { label: "End", value: formatDateTime(meeting.end_time) },
    { label: "Location", value: formatText(meeting.location) },
    { label: "Recurring", value: formatText(meeting.is_recurring) },
    { label: "Description", value: formatText(meeting.description) },
  ];

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
            <h2>Calendar details</h2>
            <p className="muted">{meeting.title}</p>
          </div>
          <button type="button" onClick={onClose}>
            Close
          </button>
        </div>

        <dl className="detail-list">
          {rows.map((row) => (
            <div key={row.label} className="detail-row">
              <dt>{row.label}</dt>
              <dd>{row.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
