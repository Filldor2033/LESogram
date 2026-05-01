import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

import { setComposerStatus, setStatus } from "../ui/status.js";

import {
    addMessage,
    handleRoomDeleted,
} from "../features/chat.js";

import { refreshMentionUsers } from "../features/mentions.js";
import { maybeNotify, showNotification } from "../features/notifications.js";
import { loadRoomUsers } from "../features/users.js";

import {
    removeMessageFromChat,
    updateMessageInChat,
    updateMessageReactions,
} from "../ui/messages-ui.js";

import { toggleChatEmptyState } from "../ui/empty-state.js";

function handleTypingPayload(payload) {
    const username = payload.username;

    if (!username || username === state.currentUser) return;

    if (payload.is_typing) {
        state.typingUsers.set(username, Date.now() + 2500);
    } else {
        state.typingUsers.delete(username);
    }

    renderTypingIndicator();
}

function renderTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");

    if (!indicator) return;

    const now = Date.now();

    for (const [username, expiresAt] of state.typingUsers.entries()) {
        if (expiresAt <= now) {
            state.typingUsers.delete(username);
        }
    }

    const users = Array.from(state.typingUsers.keys());

    if (!users.length) {
        indicator.classList.add("hidden");
        indicator.textContent = "";
        return;
    }

    indicator.classList.remove("hidden");

    if (users.length === 1) {
        indicator.textContent = t("typingOne", { user: users[0] });
    } else {
        indicator.textContent = t("typingMany", { users: users.join(", ") });
    }

    clearTimeout(state.typingRenderTimer);

    state.typingRenderTimer = setTimeout(renderTypingIndicator, 1000);
}

function handleMention(payload) {
    const text = `${payload.from}: ${payload.text}`;

    showNotification(t("mentionTitle"), text);

    if (payload.room !== state.currentRoom) {
        setStatus("roomStatus", t("mentionStatus", { user: payload.from }), false);
    }
}

function usersPopupIsOpen() {
    const popup = document.getElementById("usersPopup");

    return popup && !popup.classList.contains("hidden");
}

export function connectWS() {
    if (state.ws) {
        state.suppressNextWsCloseStatus = true;
        state.ws.close();
    }

    const roomAtConnect = state.currentRoom;
    const tokenAtConnect = state.currentRoomToken;

    const protocol = location.protocol === "https:" ? "wss" : "ws";

    const socket = new WebSocket(
        `${protocol}://${location.host}/ws/${encodeURIComponent(roomAtConnect)}?room_token=${encodeURIComponent(tokenAtConnect)}`
    );

    state.ws = socket;

    socket.onmessage = async (event) => {
        if (socket !== state.ws) return;
        if (roomAtConnect !== state.currentRoom) return;

        let payload;

        try {
            payload = JSON.parse(event.data);
        } catch {
            return;
        }

        if (payload.room && payload.room !== state.currentRoom) return;

        if (payload.type === "ping") {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    type: "pong",
                    timestamp: new Date().toISOString(),
                }));
            }
            return;
        }

        if (
            payload.type === "system" &&
            payload.system_event === "room_deleted" &&
            payload.room === state.currentRoom
        ) {
            await handleRoomDeleted(payload);
            return;
        }

        if (payload.type === "typing") {
            handleTypingPayload(payload);
            return;
        }

        if (payload.type === "mention") {
            handleMention(payload);
            return;
        }

        if (payload.type === "message_edited") {
            updateMessageInChat(payload.message);
            return;
        }

        if (payload.type === "message_reactions_updated") {
            updateMessageReactions(payload.message_id, payload.reactions);
            return;
        }

        if (payload.type === "message_deleted") {
            removeMessageFromChat(payload.message_id);
            toggleChatEmptyState();
            return;
        }

        if (payload.type === "system") {
            if (["joined", "left"].includes(payload.system_event)) {
                refreshMentionUsers();

                if (usersPopupIsOpen()) {
                    loadRoomUsers();
                }
            }

            addMessage(payload);
            return;
        }

        maybeNotify(payload);

        addMessage(payload);

        if (usersPopupIsOpen()) {
            loadRoomUsers();
        }
    };

    socket.onclose = () => {
        if (socket !== state.ws) return;

        if (state.suppressNextWsCloseStatus) {
            state.suppressNextWsCloseStatus = false;
            return;
        }

        if (state.currentRoom) {
            setComposerStatus(t("realtimeClosed"), true);
        }
    };

    socket.onopen = () => {
        if (socket !== state.ws) return;

        setComposerStatus("");
    };
}