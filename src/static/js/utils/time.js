import { state } from "../state.js";

export function formatTime(iso) {
    if (!iso) return "";

    const d = new Date(iso);
    const locale = state.currentLanguage === "ru" ? "ru-RU" : "en-US";

    return d.toLocaleTimeString(locale, {
        hour: "2-digit",
        minute: "2-digit",
    });
}