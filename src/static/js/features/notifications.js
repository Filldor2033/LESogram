import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import { updateNotificationsButton } from "../ui/notifications-ui.js";
import { setComposerStatus } from "../ui/status.js";

export async function toggleNotifications() {
    if (!("Notification" in window)) {
        setComposerStatus("Notifications not supported", true);
        return;
    }

    if (state.notificationsEnabled) {
        state.notificationsEnabled = false;
        localStorage.setItem("notifications_enabled", "0");
        updateNotificationsButton();
        return;
    }

    const permission = await Notification.requestPermission();

    if (permission === "granted") {
        state.notificationsEnabled = true;
        localStorage.setItem("notifications_enabled", "1");
        updateNotificationsButton();
    }
}

export function notificationAllowed() {
    if (!state.notificationsEnabled) return false;
    if (!("Notification" in window)) return false;
    if (Notification.permission !== "granted") return false;

    return document.hidden;
}

export function showNotification(title, body) {
    if (notificationAllowed()) {
        new Notification(title, { body });
    }
}

export function maybeNotify(payload) {
    if (!notificationAllowed()) return false;

    if (!payload || payload.type !== "message") return false;
    if (payload.username === state.currentUser) return false;

    const roomName = payload.room || state.currentRoom;
    const body = payload.text || payload.file_name || t("attachmentLabel");

    new Notification(t("newMessageTitle", { room: roomName }), {
        body,
        tag: `room-${roomName}-${payload.id || Date.now()}`,
        renotify: true,
    });

    return true;
}