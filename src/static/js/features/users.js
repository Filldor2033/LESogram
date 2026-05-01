import { loadRoomUsersRequest } from "../api/rooms-api.js";
import { getApiErrorMessage } from "../i18n/api-errors.js";
import { formatUserCount, t } from "../i18n/i18n.js";
import { state } from "../state.js";

import {
    closeUsersPopup,
    renderUsersList,
} from "../ui/users-ui.js";

export async function loadRoomUsers() {
    if (!state.currentRoom || !state.currentRoomToken) return;

    const list = document.getElementById("usersList");
    const subtitle = document.getElementById("usersPopupSubtitle");
    const title = document.getElementById("usersPopupTitle");

    if (!list || !subtitle) return;

    if (title) {
        title.textContent = t("onlineUsers");
    }

    list.innerHTML = `<div class="users-loading">...</div>`;
    subtitle.textContent = formatUserCount(0);

    try {
        const { res, data } = await loadRoomUsersRequest(
            state.currentRoom,
            state.currentRoomToken
        );

        if (!res.ok) {
            list.innerHTML = `<div class="users-empty">${getApiErrorMessage(data, "cannotLoadRooms")}</div>`;
            subtitle.textContent = formatUserCount(0);
            return;
        }

        subtitle.textContent = formatUserCount(data.count || 0);
        renderUsersList(data.users || []);
    } catch {
        list.innerHTML = `<div class="users-empty">${t("cannotLoadRooms")}</div>`;
        subtitle.textContent = formatUserCount(0);
    }
}

export function toggleUsersPopup() {
    const popup = document.getElementById("usersPopup");

    if (!popup) return;

    const willOpen = popup.classList.contains("hidden");

    if (willOpen) {
        popup.classList.remove("hidden");
        loadRoomUsers();
    } else {
        popup.classList.add("hidden");
    }
}

export { closeUsersPopup };
