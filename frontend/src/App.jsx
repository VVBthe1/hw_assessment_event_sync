import { useEffect, useState } from "react";
import { fetchConflicts, fetchMeetings } from "./api.js";
import MeetingList from "./MeetingList.jsx";
import ConflictModal from "./ConflictModal.jsx";
import CalendarModal from "./CalendarModal.jsx";

const PAGE_SIZE_OPTIONS = [10, 20, 50];

export default function App() {
  // Meetings for the current page
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cursor pagination:
  // - cursors[page] is the cursor used to load that page (null = first page)
  // - nextCursor comes from the API and is used to go to the next page
  const [cursors, setCursors] = useState([null]);
  const [page, setPage] = useState(0);
  const [nextCursor, setNextCursor] = useState(null);
  const [pageSize, setPageSize] = useState(10);

  // Conflict modal state
  const [conflictMeeting, setConflictMeeting] = useState(null);
  const [conflicts, setConflicts] = useState([]);
  const [conflictsLoading, setConflictsLoading] = useState(false);
  const [conflictsError, setConflictsError] = useState(null);

  // Calendar details modal (uses fields already on the meeting)
  const [calendarMeeting, setCalendarMeeting] = useState(null);

  // Load meetings whenever the page or page size changes
  useEffect(() => {
    let cancelled = false;

    async function loadMeetings() {
      setLoading(true);
      setError(null);

      try {
        const cursor = cursors[page];
        const data = await fetchMeetings(cursor, pageSize);

        if (cancelled) return;

        setMeetings(data.items);
        setNextCursor(data.next_cursor);
      } catch (err) {
        if (cancelled) return;
        setError(err.message);
        setMeetings([]);
        setNextCursor(null);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadMeetings();

    return () => {
      cancelled = true;
    };
  }, [page, cursors, pageSize]);

  function handlePrev() {
    if (page === 0) return;
    setPage(page - 1);
  }

  function handleNext() {
    if (nextCursor === null) return;

    // Remember this cursor for the next page, then move forward
    const updatedCursors = cursors.slice(0, page + 1);
    updatedCursors.push(nextCursor);
    setCursors(updatedCursors);
    setPage(page + 1);
  }

  function handlePageSizeChange(event) {
    setPageSize(Number(event.target.value));
    // Page size change invalidates cursor history — start over at page 1
    setCursors([null]);
    setPage(0);
  }

  async function handleShowConflicts(meeting) {
    setConflictMeeting(meeting);
    setConflicts([]);
    setConflictsError(null);
    setConflictsLoading(true);

    try {
      const data = await fetchConflicts(meeting.id);
      setConflicts(data);
    } catch (err) {
      setConflictsError(err.message);
    } finally {
      setConflictsLoading(false);
    }
  }

  function handleCloseConflicts() {
    setConflictMeeting(null);
    setConflicts([]);
    setConflictsError(null);
  }

  function handleShowCalendar(meeting) {
    setCalendarMeeting(meeting);
  }

  function handleCloseCalendar() {
    setCalendarMeeting(null);
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Meeting Desk</h1>
        <p>Client meetings across CRM and calendar</p>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <MeetingList
        meetings={meetings}
        loading={loading}
        onShowConflicts={handleShowConflicts}
        onShowCalendar={handleShowCalendar}
      />

      <div className="list-controls">
        <div className="pagination">
          <button type="button" onClick={handlePrev} disabled={page === 0 || loading}>
            Prev
          </button>
          <span className="page-label">Page {page + 1}</span>
          <button
            type="button"
            onClick={handleNext}
            disabled={nextCursor === null || loading}
          >
            Next
          </button>
        </div>

        <label className="page-size">
          Records per page
          <select value={pageSize} onChange={handlePageSizeChange} disabled={loading}>
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>
      </div>

      {conflictMeeting && (
        <ConflictModal
          meeting={conflictMeeting}
          conflicts={conflicts}
          loading={conflictsLoading}
          error={conflictsError}
          onClose={handleCloseConflicts}
        />
      )}

      {calendarMeeting && (
        <CalendarModal meeting={calendarMeeting} onClose={handleCloseCalendar} />
      )}
    </div>
  );
}
