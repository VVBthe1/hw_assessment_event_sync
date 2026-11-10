import { API_BASE } from "./config.js";

export async function fetchMeetings(cursor, limit = 20) {
  const params = new URLSearchParams();
  params.set("limit", String(limit));

  if (cursor !== null && cursor !== undefined) {
    params.set("cursor", String(cursor));
  }

  const response = await fetch(`${API_BASE}/meetings?${params.toString()}`);

  if (!response.ok) {
    throw new Error("Could not load meetings");
  }

  return response.json();
}

export async function fetchConflicts(meetingId) {
  const response = await fetch(`${API_BASE}/meetings/${meetingId}/conflicts`);

  if (!response.ok) {
    throw new Error("Could not load conflicts");
  }

  return response.json();
}
