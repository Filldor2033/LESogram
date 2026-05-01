import { t } from "../i18n/i18n.js";

export function formatBytes(bytes) {
    const size = Number(bytes || 0);
    if (!size) return "";

    const units = ["B", "KB", "MB", "GB"];
    let value = size;
    let unit = units[0];

    for (let i = 0; i < units.length; i++) {
        unit = units[i];

        if (value < 1024 || i === units.length - 1) {
            break;
        }

        value /= 1024;
    }

    return `${value >= 10 ? value.toFixed(0) : value.toFixed(1)} ${unit}`;
}

export function getFileIcon(type = "") {
    if (type.includes("pdf")) return "📄";
    if (type.includes("zip") || type.includes("rar")) return "🗜️";
    if (type.includes("text")) return "📝";

    return "📎";
}

export function getAttachmentFallbackLabel() {
    return t("attachmentLabel");
}