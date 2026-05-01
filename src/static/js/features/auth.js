import {
    loadMeRequest,
    loginRequest,
    registerRequest,
} from "../api/auth-api.js";
import { getApiErrorMessage } from "../i18n/api-errors.js";
import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import {
    showLoggedInState,
    showLoggedOutState,
    updateTopAdminBadge,
} from "../ui/header-ui.js";
import { setStatus } from "../ui/status.js";
import { resetActiveRoomState } from "./chat.js";
import { loadRooms, startRoomsAutoRefresh, stopRoomsAutoRefresh } from "./rooms.js";

export async function loadMe() {
    const { res, data } = await loadMeRequest();

    if (!res.ok) {
        if (res.status === 401) {
            logout();
        }

        return false;
    }

    state.currentUser = data.username;
    state.currentIsAdmin = Boolean(data.is_admin);

    localStorage.setItem("username", state.currentUser);
    localStorage.setItem("is_admin", state.currentIsAdmin ? "1" : "0");

    return true;
}

export async function auth(mode) {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        setStatus("authStatus", t("authFill"), true);
        return;
    }

    const request = mode === "register" ? registerRequest : loginRequest;
    const { res, data } = await request(username, password);

    if (!res.ok) {
        setStatus("authStatus", getApiErrorMessage(data, "authFailed"), true);
        return;
    }

    state.token = data.access_token;
    state.currentUser = username;

    localStorage.setItem("token", state.token);
    localStorage.setItem("username", username);

    await loadMe();

    showLoggedInState();
    setStatus("authStatus", "");

    await loadRooms();
    startRoomsAutoRefresh();
}

export function logout() {
    stopRoomsAutoRefresh();

    resetActiveRoomState();

    state.token = "";
    state.currentUser = "";
    state.currentIsAdmin = false;
    state.notificationsEnabled = false;

    localStorage.removeItem("notifications_enabled");
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("is_admin");

    document.getElementById("username").value = "";
    document.getElementById("password").value = "";

    setStatus("roomStatus", "");
    showLoggedOutState();
    updateTopAdminBadge();
}