import { state } from "../state.js";

export function updateNotificationsButton() {
    const btn = document.getElementById("notificationsBtn");
    if (!btn) return;

    if (state.notificationsEnabled) {
        btn.classList.remove("secondary");
        btn.textContent = "🔔";
    } else {
        btn.classList.add("secondary");
        btn.textContent = "🔕";
    }
}