import { sendAttachmentRequest } from "../api/attachments-api.js";
import { getApiErrorMessage } from "../i18n/api-errors.js";
import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import { setComposerStatus } from "../ui/status.js";
import { formatBytes, getFileIcon } from "../utils/files.js";
import { addMessage } from "./chat.js";
import { ensureRoomSelected } from "./composer.js";

export function clearPendingAttachment() {
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

export function setPendingAttachment(file) {
    if (!file || !ensureRoomSelected()) return;

    clearPendingAttachment();

    state.pendingAttachmentFile = file;

    const preview = document.getElementById("uploadPreview");
    const media = document.getElementById("uploadPreviewMedia");
    const name = document.getElementById("uploadPreviewName");
    const meta = document.getElementById("uploadPreviewMeta");

    media.innerHTML = "";
    name.textContent = file.name;
    meta.textContent = [file.type || t("fileLabel"), formatBytes(file.size)]
        .filter(Boolean)
        .join(" | ");

    if (file.type.startsWith("image/")) {
        state.pendingAttachmentUrl = URL.createObjectURL(file);

        const img = document.createElement("img");
        img.src = state.pendingAttachmentUrl;
        img.alt = file.name;

        media.appendChild(img);
    } else if (file.type.startsWith("video/")) {
        state.pendingAttachmentUrl = URL.createObjectURL(file);

        const video = document.createElement("video");
        video.src = state.pendingAttachmentUrl;
        video.muted = true;
        video.playsInline = true;

        media.appendChild(video);
    } else {
        const fileBox = document.createElement("div");
        fileBox.className = "upload-file-preview";

        const icon = document.createElement("div");
        icon.className = "upload-file-icon";
        icon.textContent = getFileIcon(file.type || "");

        fileBox.appendChild(icon);
        media.appendChild(fileBox);
    }

    preview.classList.remove("hidden");
    document.getElementById("message").focus();
}

export async function handleAttachmentSelect(event) {
    const input = event.target;
    const file = input.files?.[0];

    input.value = "";

    if (!file) return;

    setPendingAttachment(file);
}

export function pickAttachment() {
    if (!ensureRoomSelected()) return;

    document.getElementById("attachmentInput").click();
}

export function shouldAppendHttpResponse() {
    return !state.ws || state.ws.readyState !== WebSocket.OPEN;
}

export async function sendPendingAttachment() {
    if (!state.pendingAttachmentFile || !ensureRoomSelected()) return;

    const file = state.pendingAttachmentFile;
    const caption = document.getElementById("message").value.trim();

    const formData = new FormData();
    formData.append("room_token", state.currentRoomToken);
    formData.append("text", caption);
    formData.append("file", file);

    if (state.replyTarget?.id) {
        formData.append("reply_to_id", String(state.replyTarget.id));
    }

    setComposerStatus(t("uploadingFile", { file: file.name }));

    try {
        const { res, data } = await sendAttachmentRequest(state.currentRoom, formData);

        if (!res.ok) {
            setComposerStatus(getApiErrorMessage(data, "uploadFailed"), true);
            return;
        }

        clearPendingAttachment();

        state.replyTarget = null;
        document.getElementById("replyPreview").classList.add("hidden");

        if (shouldAppendHttpResponse()) {
            addMessage(data);
        }

        document.getElementById("message").value = "";
        setComposerStatus(t("fileSent", { file: file.name }));
    } catch {
        setComposerStatus(t("uploadFailed"), true);
    }
}