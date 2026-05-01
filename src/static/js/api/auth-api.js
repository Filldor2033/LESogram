import { apiFetch, authHeaders } from "./http.js";

export function loginRequest(username, password) {
    return apiFetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
}

export function registerRequest(username, password) {
    return apiFetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
}

export function loadMeRequest() {
    return apiFetch("/me", {
        headers: authHeaders({ json: false }),
    });
}