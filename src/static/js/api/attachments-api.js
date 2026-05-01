import { apiFetch, authHeaders } from "./http.js";

export function sendAttachmentRequest(roomName, formData) {
    return apiFetch(`/rooms/${encodeURIComponent(roomName)}/attachments`, {
        method: "POST",
        headers: authHeaders({ json: false }),
        body: formData,
    });
}