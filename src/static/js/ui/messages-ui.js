import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import { formatBytes } from "../utils/files.js";
import { escapeHtml } from "../utils/html.js";
import { formatTime } from "../utils/time.js";
import { resolveAttachmentUrl } from "./attachments-ui.js";
import { openMessageContextMenu } from "./context-menu-ui.js";

export function scrollChatToBottom() {
    const chat = document.getElementById("chat");
    if (!chat) return;

    requestAnimationFrame(() => {
        chat.scrollTop = chat.scrollHeight;
    });
}

export function getMessageType(payload) {
    return payload.content_type || "text";
}

export function highlightMentions(text) {
    return escapeHtml(text).replace(
        /@([A-Za-z0-9_а-яА-ЯёЁ-]+)/g,
        '<span class="mention">@$1</span>'
    );
}

export function getSystemMessageText(payload) {
    const actor = payload.system_actor || payload.username || "";

    if (payload.system_event === "joined") {
        return t("systemJoined", { user: actor });
    }

    if (payload.system_event === "left") {
        return t("systemLeft", { user: actor });
    }

    if (payload.system_event === "room_deleted") {
        return t("systemRoomDeleted", { user: actor });
    }

    if (payload.system_event === "rate_limited") {
        return t("systemRateLimited");
    }

    return payload.text || "";
}

export function getReplyTextPreview(message) {
    if (!message) return "";

    const text = (message.text || "").trim();

    if (text) return text;
    if (message.file_name) return message.file_name;

    if (message.content_type === "image") return t("attachmentLabel");
    if (message.content_type === "gif") return t("attachmentLabel");
    if (message.content_type === "video") return t("attachmentLabel");

    return t("attachmentLabel");
}

function buildReactionsNode(payload) {
    const reactions = payload.reactions || {};
    const entries = Object.entries(reactions);

    if (!entries.length) return null;

    const box = document.createElement("div");
    box.className = "msg-reactions";

    for (const [emoji, users] of entries) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "msg-reaction";

        if (users.includes(state.currentUser)) {
            btn.classList.add("active");
        }

        btn.textContent = `${emoji} ${users.length}`;
        btn.title = users.join(", ");

        btn.addEventListener("click", (event) => {
            event.stopPropagation();

            document.dispatchEvent(
                new CustomEvent("message:react", {
                    detail: {
                        payload,
                        emoji,
                    },
                })
            );
        });

        box.appendChild(btn);
    }

    return box;
}

function buildAttachmentNode(payload) {
    const contentType = getMessageType(payload);
    const resolvedUrl = resolveAttachmentUrl(payload.media_url);

    if (!resolvedUrl || contentType === "text") {
        return null;
    }

    if (contentType === "image" || contentType === "gif") {
        const media = document.createElement("div");
        media.className = "msg-media";

        const img = document.createElement("img");
        img.src = resolvedUrl;
        img.alt = payload.file_name || t("attachmentLabel");
        img.loading = "lazy";
        img.onload = scrollChatToBottom;

        media.appendChild(img);
        return media;
    }

    if (contentType === "video") {
        const media = document.createElement("div");
        media.className = "msg-media";

        const video = document.createElement("video");
        video.src = resolvedUrl;
        video.controls = true;
        video.preload = "metadata";
        video.onloadedmetadata = scrollChatToBottom;

        media.appendChild(video);
        return media;
    }

    const fileBox = document.createElement("div");
    fileBox.className = "msg-file";

    const info = document.createElement("div");
    info.className = "msg-file-info";

    const name = document.createElement("div");
    name.className = "msg-file-name";
    name.textContent = payload.file_name || t("attachmentLabel");

    const meta = document.createElement("div");
    meta.className = "msg-file-meta";

    const metaParts = [];

    if (payload.mime_type) metaParts.push(payload.mime_type);
    if (payload.file_size) metaParts.push(formatBytes(payload.file_size));

    meta.textContent = metaParts.join(" | ") || t("fileLabel");

    const link = document.createElement("a");
    link.className = "file-link";
    link.dataset.i18nKey = "download";
    link.href = resolvedUrl;
    link.textContent = t("download");
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    if (payload.file_name) {
        link.download = payload.file_name;
    }

    info.appendChild(name);
    info.appendChild(meta);

    fileBox.appendChild(info);
    fileBox.appendChild(link);

    return fileBox;
}

export function createMessageNode(payload) {
    const div = document.createElement("div");

    if (payload.id) {
        div.dataset.messageId = String(payload.id);
    }

    if (payload.type === "system") {
        div.className = "msg system";

        if (payload.system_event) {
            div.dataset.systemEvent = payload.system_event;
        }

        if (payload.system_actor) {
            div.dataset.systemActor = payload.system_actor;
        }

        div.innerText = getSystemMessageText(payload);
        return div;
    }

    const mine = payload.username === state.currentUser;

    div.className = "msg " + (mine ? "me" : "other");

    div.addEventListener("contextmenu", (event) => {
        openMessageContextMenu(event, payload);
    });

    div.addEventListener("touchstart", (event) => {
        state.longPressTimer = setTimeout(() => {
            const touch = event.touches[0];

            openMessageContextMenu(
                {
                    preventDefault: () => event.preventDefault(),
                    clientX: touch.clientX,
                    clientY: touch.clientY,
                },
                payload
            );
        }, 550);
    });

    div.addEventListener("touchend", () => {
        clearTimeout(state.longPressTimer);
    });

    div.addEventListener("touchmove", () => {
        clearTimeout(state.longPressTimer);
    });

    const username = document.createElement("div");
    username.className = "msg-username";
    username.textContent = payload.username;

    if (payload.reply_to_id) {
        const replied = state.messageCache.get(Number(payload.reply_to_id));

        const replyBox = document.createElement("div");
        replyBox.className = "msg-reply";

        const replyAuthor = document.createElement("div");
        replyAuthor.className = "msg-reply-author";
        replyAuthor.textContent = replied?.username || t("reply");

        const replyText = document.createElement("div");
        replyText.className = "msg-reply-text";
        replyText.textContent = replied
            ? getReplyTextPreview(replied)
            : `#${payload.reply_to_id}`;

        replyBox.appendChild(replyAuthor);
        replyBox.appendChild(replyText);

        replyBox.addEventListener("click", () => {
            const target = document.querySelector(
                `.msg[data-message-id="${payload.reply_to_id}"]`
            );

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
            }
        });

        div.appendChild(replyBox);
    }

    const attachmentNode = buildAttachmentNode(payload);
    const hasText = Boolean((payload.text || "").trim());

    div.appendChild(username);

    if (attachmentNode) {
        div.appendChild(attachmentNode);
    }

    if (hasText) {
        const text = document.createElement("div");
        text.className = "msg-text";
        text.innerHTML = highlightMentions(payload.text);

        div.appendChild(text);
    }

    const reactionsNode = buildReactionsNode(payload);

    if (reactionsNode) {
        div.appendChild(reactionsNode);
    }

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.innerText = payload.is_edited
        ? `${formatTime(payload.timestamp)} · ${t("edited")}`
        : formatTime(payload.timestamp);

    div.appendChild(meta);

    return div;
}

export function updateMessageInChat(payload) {
    if (payload.id) {
        state.messageCache.set(Number(payload.id), payload);
    }

    const oldNode = document.querySelector(
        `.msg[data-message-id="${payload.id}"]`
    );

    if (!oldNode) return;

    const newNode = createMessageNode(payload);
    oldNode.replaceWith(newNode);
}

export function updateMessageReactions(messageId, reactions) {
    const id = Number(messageId);
    const payload = state.messageCache.get(id);

    if (!payload) return;

    payload.reactions = reactions || {};
    state.messageCache.set(id, payload);

    updateMessageInChat(payload);
}

export function removeMessageFromChat(messageId) {
    document.querySelectorAll(".msg[data-message-id]").forEach((node) => {
        if (node.dataset.messageId === String(messageId)) {
            node.remove();
        }
    });
}