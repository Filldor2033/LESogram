import { t } from "./i18n.js";

const API_DETAIL_MAP = {
    "Missing token": "apiMissingToken",
    "Invalid token": "apiInvalidToken",
    "User already exists": "apiUserExists",
    "Invalid credentials": "apiInvalidCredentials",
    "Room already exists": "apiRoomExists",
    "Room not found": "apiRoomNotFound",
    "Wrong room password": "apiWrongRoomPassword",
    "No access to this room": "apiNoRoomAccess",
    "Only the creator can delete this room": "apiDeleteDenied",
    "Attachment is missing a file name": "apiAttachmentMissingName",
    "Attachment not found": "apiAttachmentNotFound",
    "File type is not allowed": "apiFileTypeNotAllowed",
    "GIF uploads are disabled": "apiGifDisabled",
    "Attachment is empty": "apiAttachmentEmpty",
    "Message cannot be empty": "apiMessageEmpty",
    "Room name can contain only letters, numbers, spaces, _ and -": "apiInvalidRoomName",
    "Only the author can edit this message": "onlyAuthorCanEdit",
};

export function translateApiDetail(detail) {
    if (!detail || typeof detail !== "string") return "";

    if (API_DETAIL_MAP[detail]) {
        return t(API_DETAIL_MAP[detail]);
    }

    let match = detail.match(/^Attachment is too large\. Max size is (\d+) MB$/);
    if (match) {
        return t("apiAttachmentTooLarge", { size: match[1] });
    }

    match = detail.match(/^Message must be at most (\d+) characters$/);
    if (match) {
        return t("apiMessageTooLong", { max: match[1] });
    }

    match = detail.match(/^Too many requests\. Retry in (\d+) seconds$/);
    if (match) {
        return t("apiTooManyRequests", { seconds: match[1] });
    }

    return detail;
}

export function getApiErrorMessage(data, fallbackKey) {
    const translated = translateApiDetail(data?.detail);
    return translated || t(fallbackKey);
}