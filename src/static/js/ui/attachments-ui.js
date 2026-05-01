import { t } from "../i18n/i18n.js";
import { state } from "../state.js";
import { formatBytes, getFileIcon } from "../utils/files.js";

export function resolveAttachmentUrl(mediaUrl) {
    if (!mediaUrl) return "";

    if (!state.currentRoomToken) {
        return mediaUrl;
    }

    const separator = mediaUrl.includes("?") ? "&" : "?";
    return `${mediaUrl}${separator}room_token=${encodeURIComponent(state.currentRoomToken)}`;
}

export function renderPendingAttachmentPreview(file) {
    const preview = document.getElementById("uploadPreview");
    const media = document.getElementById("uploadPreviewMedia");
    const name = document.getElementById("uploadPreviewName");
    const meta = document.getElementById("uploadPreviewMeta");

    if (!preview || !media || !name || !meta) return;

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
}

export function clearPendingAttachmentPreview() {
    const preview = document.getElementById("uploadPreview");
    const media = document.getElementById("uploadPreviewMedia");

    if (preview) preview.classList.add("hidden");
    if (media) media.innerHTML = "";
}