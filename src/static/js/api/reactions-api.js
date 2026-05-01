import { apiFetch, authHeaders } from "./http.js";

export function reactToMessageRequest(messageId, emoji) {
    return apiFetch(`/messages/${encodeURIComponent(messageId)}/reactions`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ emoji }),
    });
}