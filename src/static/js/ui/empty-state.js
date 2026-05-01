import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

export function renderChatEmptyState() {
    const chat = document.getElementById("chat");
    if (!chat) return;

    let empty = document.getElementById("chatEmptyState");

    if (!empty) {
        empty = document.createElement("div");
        empty.id = "chatEmptyState";
        empty.className = "chat-empty";
    }

    empty.innerHTML = `
        <div class="chat-empty-title">
            ${state.currentRoom ? t("emptyNoMessagesTitle") : t("emptyNoRoomTitle")}
        </div>
        <div class="chat-empty-text">
            ${state.currentRoom ? t("emptyNoMessagesText") : t("emptyNoRoomText")}
        </div>
    `;

    if (!empty.parentElement) {
        chat.appendChild(empty);
    }
}

export function toggleChatEmptyState() {
    const empty = document.getElementById("chatEmptyState");
    const chat = document.getElementById("chat");

    if (!empty || !chat) return;

    const hasRealMessages = Array
        .from(chat.children)
        .some(node => node.id !== "chatEmptyState");

    empty.classList.toggle("hidden", hasRealMessages);
}