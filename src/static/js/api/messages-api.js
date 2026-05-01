import { apiFetch, authHeaders } from "./http.js";

export function loadMessagesRequest(roomName, roomToken, beforeId = null) {
    let url = `/messages/${encodeURIComponent(roomName)}?room_token=${encodeURIComponent(roomToken)}`;

    if (beforeId) {
        url += `&before_id=${encodeURIComponent(beforeId)}`;
    }

    return apiFetch(url);
}

export function editMessageRequest(messageId, text) {
    return apiFetch(`/messages/${encodeURIComponent(messageId)}`, {
        method: "PATCH",
        headers: authHeaders(),
        body: JSON.stringify({ text }),
    });
}

export function deleteMessageRequest(messageId) {
    return apiFetch(`/messages/${encodeURIComponent(messageId)}`, {
        method: "DELETE",
        headers: authHeaders({ json: false }),
    });
}