import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

export function openMessageContextMenu(event, payload) {
    event.preventDefault();

    state.contextMessage = payload;

    const menu = document.getElementById("messageContextMenu");
    const deleteBtn = document.getElementById("contextDeleteBtn");
    const editBtn = document.getElementById("contextEditBtn");
    const replyBtn = document.getElementById("contextReplyBtn");

    if (!menu) return;

    if (editBtn) {
        editBtn.classList.toggle(
            "hidden",
            !(payload.id && payload.username === state.currentUser && payload.content_type === "text")
        );

        editBtn.textContent = t("edit");
    }

    if (deleteBtn) {
        deleteBtn.classList.toggle("hidden", !(state.currentIsAdmin && payload.id));
        deleteBtn.textContent = t("delete");
    }

    if (replyBtn) {
        replyBtn.textContent = t("reply");
    }

    menu.classList.remove("hidden");

    const menuRect = menu.getBoundingClientRect();
    const padding = 8;

    let x = event.clientX;
    let y = event.clientY;

    if (x + menuRect.width > window.innerWidth - padding) {
        x = window.innerWidth - menuRect.width - padding;
    }

    if (y + menuRect.height > window.innerHeight - padding) {
        y = window.innerHeight - menuRect.height - padding;
    }

    menu.style.left = `${Math.max(padding, x)}px`;
    menu.style.top = `${Math.max(padding, y)}px`;
}

export function closeMessageContextMenu() {
    const menu = document.getElementById("messageContextMenu");

    if (menu) {
        menu.classList.add("hidden");
    }

    state.contextMessage = null;
}