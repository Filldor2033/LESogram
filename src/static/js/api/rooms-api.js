import { apiFetch, authHeaders } from "./http.js";

export function loadRoomsRequest() {
    return apiFetch("/rooms", {
        headers: authHeaders({ json: false }),
    });
}

export function createRoomRequest(name, password) {
    return apiFetch("/rooms", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ name, password }),
    });
}

export function joinRoomRequest(room, password) {
    return apiFetch("/rooms/join", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ room, password }),
    });
}

export function deleteRoomRequest(roomName) {
    return apiFetch(`/rooms/${encodeURIComponent(roomName)}`, {
        method: "DELETE",
        headers: authHeaders({ json: false }),
    });
}

export function loadRoomUsersRequest(roomName, roomToken) {
    return apiFetch(
        `/rooms/${encodeURIComponent(roomName)}/users?room_token=${encodeURIComponent(roomToken)}`
    );
}