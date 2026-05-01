import { state } from "../state.js";

export function authHeaders(options = {}) {
    const headers = {
        Authorization: "Bearer " + state.token,
    };

    if (options.json !== false) {
        headers["Content-Type"] = "application/json";
    }

    return headers;
}

export async function safeJson(res) {
    try {
        return await res.json();
    } catch {
        return {};
    }
}

export async function apiFetch(url, options = {}) {
    const res = await fetch(url, options);
    const data = await safeJson(res);

    return {
        res,
        data,
        ok: res.ok,
        status: res.status,
    };
}