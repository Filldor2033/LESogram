import { getApiErrorMessage } from "../i18n/api-errors.js";
import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

import {
    deleteMessageRequest,
    editMessageRequest,
} from "../api/messages-api.js";

import { reactToMessageRequest } from "../api/reactions-api.js";

import { closeMessageContextMenu } from "../ui/context-menu-ui.js";
import { setComposerStatus } from "../ui/status.js";

import {
    getReplyTextPreview,
    removeMessageFromChat,
    updateMessageInChat,
    updateMessageReactions,
} from "../ui/messages-ui.js";

import { toggleChatEmptyState } from "../ui/empty-state.js";

export function setReplyTarget(messageId) {
    const message = state.messageCache.get(Number(messageId));

    if (!message) return;

    state.replyTarget = message;

    const title = document.getElementById("replyPreviewTitle");
    const text = document.getElementById("replyPreviewText");
    const preview = document.getElementById("replyPreview");
    const input = document.getElementById("message");

    if (title) title.textContent = message.username;
    if (text) text.textContent = getReplyTextPreview(message);
    if (preview) preview.classList.remove("hidden");
    if (input) input.focus();
}

export function clearReplyTarget() {
    state.replyTarget = null;

    const preview = document.getElementById("replyPreview");

    if (preview) {
        preview.classList.add("hidden");
    }
}

export function contextReply() {
    if (state.contextMessage?.id) {
        setReplyTarget(state.contextMessage.id);
    }

    closeMessageContextMenu();
}

export function contextDelete() {
    if (state.contextMessage?.id && state.currentIsAdmin) {
        deleteMessage(state.contextMessage.id);
    }

    closeMessageContextMenu();
}

export function contextEdit() {
    if (state.contextMessage?.id) {
        startEditingMessage(state.contextMessage.id);
    }

    closeMessageContextMenu();
}

export async function contextReact(emoji, payload = state.contextMessage) {
    if (!payload?.id) return;

    try {
        const { res, data } = await reactToMessageRequest(payload.id, emoji);

        if (!res.ok) {
            setComposerStatus(getApiErrorMessage(data, "cannotLoadMessages"), true);
            return;
        }

        updateMessageReactions(data.message_id, data.reactions);
    } catch {
        setComposerStatus(t("cannotLoadMessages"), true);
    } finally {
        closeMessageContextMenu();
    }
}

export function startEditingMessage(messageId) {
    const node = document.querySelector(`.msg[data-message-id="${messageId}"]`);
    const payload = state.messageCache.get(Number(messageId));

    if (!node || !payload) return;

    const textNode = node.querySelector(".msg-text");

    if (!textNode) return;

    const oldText = payload.text || "";

    const editor = document.createElement("div");
    editor.className = "msg-editor";

    const input = document.createElement("textarea");
    input.className = "msg-editor-input";
    input.value = oldText;

    const actions = document.createElement("div");
    actions.className = "msg-editor-actions";

    const saveBtn = document.createElement("button");
    saveBtn.className = "small-btn";
    saveBtn.type = "button";
    saveBtn.dataset.i18nKey = "save";
    saveBtn.textContent = t("save");

    const cancelBtn = document.createElement("button");
    cancelBtn.className = "secondary small-btn";
    cancelBtn.type = "button";
    cancelBtn.dataset.i18nKey = "cancel";
    cancelBtn.textContent = t("cancel");

    actions.appendChild(saveBtn);
    actions.appendChild(cancelBtn);

    editor.appendChild(input);
    editor.appendChild(actions);

    textNode.replaceWith(editor);
    input.focus();

    cancelBtn.addEventListener("click", () => {
        editor.replaceWith(textNode);
    });

    saveBtn.addEventListener("click", async () => {
        await submitEditMessage(messageId, input.value);
    });
}

export async function submitEditMessage(messageId, text) {
    const cleanText = text.trim();

    if (!cleanText) {
        setComposerStatus(t("apiMessageEmpty"), true);
        return;
    }

    const { res, data } = await editMessageRequest(messageId, cleanText);

    if (!res.ok) {
        setComposerStatus(getApiErrorMessage(data, "cannotEditMessage"), true);
        return;
    }

    if (data.message) {
        updateMessageInChat(data.message);
    }
}

export async function deleteMessage(messageId) {
    if (!state.currentIsAdmin) return;

    const { res, data } = await deleteMessageRequest(messageId);

    if (!res.ok) {
        setComposerStatus(getApiErrorMessage(data, "cannotDeleteRoom"), true);
        return;
    }

    removeMessageFromChat(messageId);
    toggleChatEmptyState();
}

export function bindMessageActionEvents() {
    document.getElementById("contextReplyBtn")?.addEventListener("click", contextReply);
    document.getElementById("contextEditBtn")?.addEventListener("click", contextEdit);
    document.getElementById("contextDeleteBtn")?.addEventListener("click", contextDelete);

    document.querySelectorAll("[data-context-reaction]").forEach((button) => {
        button.addEventListener("click", () => {
            contextReact(button.dataset.contextReaction);
        });
    });

    document.addEventListener("message:react", (event) => {
        const { payload, emoji } = event.detail || {};

        if (!payload || !emoji) return;

        contextReact(emoji, payload);
    });
}