const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function sendChatMessage(message, formState, history) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      form_state: formState,
      history: history.map((m) => ({ role: m.role, content: m.content })),
    }),
  });
  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchInteractions() {
  const res = await fetch(`${BASE_URL}/interactions`);
  if (!res.ok) throw new Error(`Failed to load interactions: ${res.status}`);
  return res.json();
}

export async function submitInteraction(formState) {
  const res = await fetch(`${BASE_URL}/interactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ form_state: formState }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || "Submission failed");
  }
  return body;
}
