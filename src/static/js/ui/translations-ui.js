import { formatUserCount, t } from "../i18n/i18n.js";
import { state } from "../state.js";

import {
    updateChatHeader,
    updateRoomsCount,
    updateTopAdminBadge,
} from "./header-ui.js";

import {
    renderChatEmptyState,
    toggleChatEmptyState,
} from "./empty-state.js";
import { updateNotificationsButton } from "./notifications-ui.js";
import { renderRooms, setRoomsListCollapsed } from "./rooms-ui.js";

import { deleteRoom, joinRoom } from "../features/rooms.js";
import { closeMessageContextMenu } from "./context-menu-ui.js";

function setButtonText(id, key, vars = {}) {
    const el = document.getElementById(id);

    if (el) {
        el.textContent = t(key, vars);
    }
}

function setInputPlaceholder(id, key) {
    const el = document.getElementById(id);

    if (el) {
        el.placeholder = t(key);
    }
}

function updateLanguageButtons() {
    const enBtn = document.getElementById("langEnBtn");
    const ruBtn = document.getElementById("langRuBtn");

    if (enBtn) {
        enBtn.classList.toggle("active", state.currentLanguage === "en");
    }

    if (ruBtn) {
        ruBtn.classList.toggle("active", state.currentLanguage === "ru");
    }
}

function refreshRuntimeTranslations() {
    document
        .querySelectorAll(".system[data-system-event][data-system-actor]")
        .forEach((node) => {
            const event = node.dataset.systemEvent;
            const actor = node.dataset.systemActor;

            const key = event === "joined"
                ? "systemJoined"
                : event === "left"
                    ? "systemLeft"
                    : "systemRoomDeleted";

            node.textContent = t(key, { user: actor });
        });

    document
        .querySelectorAll(".file-link[data-i18n-key='download']")
        .forEach((node) => {
            node.textContent = t("download");
        });

    const cancelPendingAttachment = document.getElementById("cancelPendingAttachment");

    if (cancelPendingAttachment) {
        cancelPendingAttachment.textContent = t("cancel");
    }
}

export function applyTranslations() {
    document.documentElement.lang = state.currentLanguage;
    document.title = t("appTitle");

    const directTextNodes = {
        brandSubtitle: "brandSubtitle",
        authTitle: "authTitle",
        createRoomTitle: "createRoomTitle",
        roomListTitle: "roomListTitle",
        roomListSubtitle: "roomListSubtitle",
        onlineFilterAll: "allRooms",
        onlineFilterOnline: "onlineOnly",
        onlineFilterEmpty: "emptyOnly",
        sortNameAsc: "sortNameAsc",
        sortNameDesc: "sortNameDesc",
        sortOnlineDesc: "sortOnlineDesc",
        sortOnlineAsc: "sortOnlineAsc",
        sortCreatorAsc: "sortCreatorAsc",
    };

    for (const [id, key] of Object.entries(directTextNodes)) {
        const el = document.getElementById(id);

        if (el) {
            el.textContent = t(key);
        }
    }

    setButtonText("loginBtn", "login");
    setButtonText("registerBtn", "register");
    setButtonText("logoutBtn", "logout");
    setButtonText("createRoomBtn", "createRoom");
    setButtonText("refreshRoomsBtn", "refreshRooms");
    setButtonText("resetFiltersBtn", "resetFilters");
    setButtonText("leaveChatBtn", "leaveChat");
    setButtonText("sendBtn", "send");
    setButtonText("contextReplyBtn", "reply");
    setButtonText("contextEditBtn", "edit");
    setButtonText("contextDeleteBtn", "delete");
    setButtonText("roomUsersBtn", "users");

    document.querySelectorAll("[data-i18n-key]").forEach((node) => {
        node.textContent = t(node.dataset.i18nKey);
    });

    const attachBtn = document.getElementById("pickAttachmentBtn");

    if (attachBtn) {
        attachBtn.title = t("attachmentLabel");
    }

    const usersPopupSubtitle = document.getElementById("usersPopupSubtitle");

    if (usersPopupSubtitle) {
        const currentCount = document.querySelectorAll("#usersList .user-item").length;
        usersPopupSubtitle.textContent = formatUserCount(currentCount);
    }

    setInputPlaceholder("username", "usernamePlaceholder");
    setInputPlaceholder("password", "passwordPlaceholder");
    setInputPlaceholder("newRoomName", "newRoomNamePlaceholder");
    setInputPlaceholder("newRoomPassword", "roomPasswordPlaceholder");
    setInputPlaceholder("roomSearch", "roomSearchPlaceholder");
    setInputPlaceholder("creatorSearch", "creatorSearchPlaceholder");
    setInputPlaceholder("message", "messagePlaceholder");

    updateLanguageButtons();
    updateChatHeader();
    updateRoomsCount();
    updateTopAdminBadge();

    renderChatEmptyState();
    toggleChatEmptyState();

    refreshRuntimeTranslations();
    setRoomsListCollapsed(state.roomsListCollapsed);

    closeMessageContextMenu();
    renderRooms({
        onJoinRoom: joinRoom,
        onDeleteRoom: deleteRoom
    });
    updateNotificationsButton();
}