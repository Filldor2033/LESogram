import { formatRoomCount, t } from "../i18n/i18n.js";
import { state } from "../state.js";

export function updateTopAdminBadge() {
    const badge = document.getElementById("adminTopBadge");
    if (!badge) return;

    badge.textContent = `👑 ${t("adminBadge")}`;
    badge.classList.toggle("hidden", !state.currentIsAdmin);
}

export function updateChatHeader() {
    const title = document.getElementById("chatHeader");
    const subtitle = document.getElementById("chatSubheader");

    if (title) {
        title.innerText = state.currentRoom
            ? t("roomHeader", { room: state.currentRoom })
            : t("chatNotSelected");
    }

    if (subtitle) {
        subtitle.innerText = state.currentRoom
            ? t("realtimeActive")
            : t("chooseRoom");
    }
}

export function updateRoomsCount() {
    const pill = document.getElementById("roomsCountPill");
    if (!pill) return;

    pill.textContent = formatRoomCount(state.allRooms.length);
}

export function showLoggedInState() {
    document.getElementById("authSection").classList.add("hidden");
    document.getElementById("roomsSection").classList.remove("hidden");
    document.getElementById("whoami").innerText = state.currentUser;

    updateTopAdminBadge();
}

export function showLoggedOutState() {
    document.getElementById("authSection").classList.remove("hidden");
    document.getElementById("roomsSection").classList.add("hidden");
}