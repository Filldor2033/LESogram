import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import { setComposerStatus } from "../ui/status.js";
import { sendPendingAttachment } from "./attachments.js";
import {
    closeMentionDropdown,
    getVisibleMentionOptions,
    insertMention,
    renderMentionDropdown,
} from "./mentions.js";

export function ensureRoomSelected() {
    if (!state.currentRoom || !state.currentRoomToken) {
        setComposerStatus(t("joinRoomFirst"), true);
        return false;
    }

    return true;
}

export function sendTypingState(isTyping) {
    if (!state.ws || state.ws.readyState !== WebSocket.OPEN || !state.currentRoom) {
        return;
    }

    state.ws.send(JSON.stringify({
        type: "typing",
        is_typing: isTyping,
    }));
}

export function handleMessageInputTyping() {
    sendTypingState(true);

    clearTimeout(state.typingStopTimer);

    state.typingStopTimer = setTimeout(() => {
        sendTypingState(false);
    }, 1200);
}

export function handleComposerInput() {
    handleMessageInputTyping();
    state.mentionDropdownIndex = 0;
    renderMentionDropdown();
}

export function handleComposerKey(event) {
    const dropdown = document.getElementById("mentionDropdown");

    if (dropdown && !dropdown.classList.contains("hidden")) {
        const options = getVisibleMentionOptions();

        if (event.key === "ArrowDown") {
            event.preventDefault();
            state.mentionDropdownIndex = (state.mentionDropdownIndex + 1) % options.length;
            renderMentionDropdown();
            return;
        }

        if (event.key === "ArrowUp") {
            event.preventDefault();
            state.mentionDropdownIndex =
                (state.mentionDropdownIndex - 1 + options.length) % options.length;
            renderMentionDropdown();
            return;
        }

        if (event.key === "Enter" || event.key === "Tab") {
            event.preventDefault();
            insertMention(options[state.mentionDropdownIndex]);
            return;
        }

        if (event.key === "Escape") {
            event.preventDefault();
            closeMentionDropdown();
            return;
        }
    }

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

export async function sendMessage() {
    if (!ensureRoomSelected()) return;

    if (state.pendingAttachmentFile) {
        await sendPendingAttachment();
        return;
    }

    const input = document.getElementById("message");
    const text = input.value.trim();

    if (!text || !state.ws || state.ws.readyState !== WebSocket.OPEN) {
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
            setComposerStatus(t("realtimeNotReady"), true);
        }

        return;
    }

    state.ws.send(JSON.stringify({
        text,
        reply_to_id: state.replyTarget?.id || null,
    }));

    sendTypingState(false);
    clearTimeout(state.typingStopTimer);

    input.value = "";

    const replyPreview = document.getElementById("replyPreview");
    if (replyPreview) {
        replyPreview.classList.add("hidden");
    }

    state.replyTarget = null;

    setComposerStatus("");
}