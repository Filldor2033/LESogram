import { getApiErrorMessage } from "../i18n/api-errors.js";
import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

import { loadMessagesRequest } from "../api/messages-api.js";

import { updateChatHeader } from "../ui/header-ui.js";
import { setRoomsListCollapsed } from "../ui/rooms-ui.js";
import { setComposerStatus, setStatus } from "../ui/status.js";

import {
    createMessageNode,
    removeMessageFromChat,
    scrollChatToBottom,
} from "../ui/messages-ui.js";

import {
    renderChatEmptyState,
    toggleChatEmptyState,
} from "../ui/empty-state.js";

import { closeUsersPopup } from "../ui/users-ui.js";
import { closeMentionDropdown } from "./mentions.js";

function clearPendingAttachmentLocal() {
    state.pendingAttachmentFile = null;

    if (state.pendingAttachmentUrl) {
        URL.revokeObjectURL(state.pendingAttachmentUrl);
        state.pendingAttachmentUrl = "";
    }

    const preview = document.getElementById("uploadPreview");
    const media = document.getElementById("uploadPreviewMedia");

    if (preview) preview.classList.add("hidden");
    if (media) media.innerHTML = "";
}

export function addMessage(payload) {
    const chat = document.getElementById("chat");

    if (!chat) return;

    const div = createMessageNode(payload);

    if (payload.id) {
        state.messageCache.set(Number(payload.id), payload);
    }

    chat.appendChild(div);

    toggleChatEmptyState();
    scrollChatToBottom();
}

export function clearChat() {
    const chat = document.getElementById("chat");

    if (!chat) return;

    chat.innerHTML = "";

    renderChatEmptyState();
    toggleChatEmptyState();
}

export async function loadMessages({ older = false } = {}) {
    if (state.messagesLoading) return;

    state.messagesLoading = true;

    const chat = document.getElementById("chat");

    if (!chat) {
        state.messagesLoading = false;
        return;
    }

    const oldScrollHeight = chat.scrollHeight;
    const oldScrollTop = chat.scrollTop;

    try {
        const beforeId = older ? state.messagesNextBeforeId : null;

        const { res, data } = await loadMessagesRequest(
            state.currentRoom,
            state.currentRoomToken,
            beforeId
        );

        if (!res.ok) {
            setStatus("roomStatus", getApiErrorMessage(data, "cannotLoadMessages"), true);
            return;
        }

        const messages = data.messages || [];

        state.messagesNextBeforeId = data.next_before_id;
        state.messagesHasMore = Boolean(data.has_more);

        if (older) {
            const fragment = document.createDocumentFragment();

            for (const message of messages) {
                if (message.id) {
                    state.messageCache.set(Number(message.id), message);
                }

                fragment.appendChild(createMessageNode(message));
            }

            chat.insertBefore(fragment, chat.firstChild);
            toggleChatEmptyState();

            const newScrollHeight = chat.scrollHeight;
            chat.scrollTop = newScrollHeight - oldScrollHeight + oldScrollTop;
        } else {
            for (const message of messages) {
                addMessage(message);
            }

            scrollChatToBottom();
        }
    } catch {
        setStatus("roomStatus", t("cannotLoadMessages"), true);
    } finally {
        state.messagesLoading = false;
    }
}

export function handleChatScroll() {
    const chat = document.getElementById("chat");

    if (!chat) return;

    if (
        state.currentRoom &&
        state.currentRoomToken &&
        state.messagesHasMore &&
        !state.messagesLoading &&
        chat.scrollTop < 80
    ) {
        loadMessages({ older: true });
    }
}

export function resetActiveRoomState() {
    if (state.ws) {
        state.suppressNextWsCloseStatus = true;
        state.ws.close();
        state.ws = null;
    }

    state.currentRoom = "";
    state.currentRoomToken = "";

    state.replyTarget = null;
    state.messageCache.clear();

    const replyPreview = document.getElementById("replyPreview");

    if (replyPreview) {
        replyPreview.classList.add("hidden");
    }

    state.mentionUsers = [];
    closeMentionDropdown();

    clearPendingAttachmentLocal();

    state.typingUsers.clear();

    clearTimeout(state.typingStopTimer);
    clearTimeout(state.typingRenderTimer);

    const typingIndicator = document.getElementById("typingIndicator");

    if (typingIndicator) {
        typingIndicator.classList.add("hidden");
        typingIndicator.textContent = "";
    }

    updateChatHeader();

    document.getElementById("leaveChatBtn")?.classList.add("hidden");
    document.getElementById("roomUsersBtn")?.classList.add("hidden");

    closeUsersPopup();

    const input = document.getElementById("message");

    if (input) {
        input.value = "";
    }

    clearChat();
    setRoomsListCollapsed(false);
    setComposerStatus("");
}

export async function handleRoomDeleted(payload) {
    const deletedRoom = payload.room || state.currentRoom;
    const actor = payload.system_actor || "";
    const ownDeletion = actor === state.currentUser;

    resetActiveRoomState();

    setStatus(
        "roomStatus",
        ownDeletion
            ? t("deletedRoom", { room: deletedRoom })
            : t("roomDeletedByOwner", { room: deletedRoom })
    );

    const { loadRooms } = await import("./rooms.js");
    await loadRooms();
}

export { removeMessageFromChat };
