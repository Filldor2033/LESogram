import { state } from "./state.js";

import { getInitialLanguage, setLanguage } from "./i18n/i18n.js";

import {
    clearPendingAttachment,
    handleAttachmentSelect,
    pickAttachment,
    setPendingAttachment,
} from "./features/attachments.js";
import { auth, loadMe, logout } from "./features/auth.js";
import { clearChat, handleChatScroll } from "./features/chat.js";
import {
    handleComposerInput,
    handleComposerKey,
    sendMessage,
} from "./features/composer.js";
import { bindMessageActionEvents, clearReplyTarget } from "./features/message-actions.js";
import { toggleNotifications } from "./features/notifications.js";
import {
    createRoom,
    deleteRoom,
    joinRoom,
    leaveChat,
    loadRooms,
    startRoomsAutoRefresh,
} from "./features/rooms.js";
import { closeUsersPopup, toggleUsersPopup } from "./features/users.js";

import { closeMessageContextMenu } from "./ui/context-menu-ui.js";
import { showLoggedInState } from "./ui/header-ui.js";
import { renderRooms, resetRoomFilters, toggleRoomsList } from "./ui/rooms-ui.js";
import { applyTranslations } from "./ui/translations-ui.js";

state.currentLanguage = getInitialLanguage();

function toggleChatFullscreen() {
    state.chatFullscreen = !state.chatFullscreen;

    document.body.classList.toggle("chat-fullscreen-mode", state.chatFullscreen);

    const btn = document.getElementById("fullscreenChatBtn");

    if (btn) {
        btn.textContent = state.chatFullscreen ? "⮌" : "⛶";
    }
}

async function initializeSession() {
    applyTranslations();
    clearChat();

    if (!state.token || !state.currentUser) return;

    const ok = await loadMe();
    if (!ok) return;

    showLoggedInState();

    await loadRooms();
    startRoomsAutoRefresh();
}

function bindEvents() {
    document.getElementById("loginBtn")?.addEventListener("click", () => auth("login"));
    document.getElementById("registerBtn")?.addEventListener("click", () => auth("register"));
    document.getElementById("logoutBtn")?.addEventListener("click", logout);

    document.getElementById("createRoomBtn")?.addEventListener("click", createRoom);
    document.getElementById("refreshRoomsBtn")?.addEventListener("click", loadRooms);
    document.getElementById("resetFiltersBtn")?.addEventListener("click", resetRoomFilters);
    document.getElementById("toggleRoomsBtn")?.addEventListener("click", toggleRoomsList);

    document.getElementById("leaveChatBtn")?.addEventListener("click", leaveChat);
    document.getElementById("roomUsersBtn")?.addEventListener("click", toggleUsersPopup);

    document.getElementById("sendBtn")?.addEventListener("click", sendMessage);
    document.getElementById("message")?.addEventListener("keydown", handleComposerKey);
    document.getElementById("message")?.addEventListener("input", handleComposerInput);

    document.getElementById("pickAttachmentBtn")?.addEventListener("click", pickAttachment);
    document.getElementById("attachmentInput")?.addEventListener("change", handleAttachmentSelect);
    document.getElementById("cancelPendingAttachment")?.addEventListener("click", clearPendingAttachment);

    document.getElementById("closeUsersPopupBtn")?.addEventListener("click", closeUsersPopup);
    document.getElementById("clearReplyTargetBtn")?.addEventListener("click", clearReplyTarget);

    document.getElementById("fullscreenChatBtn")?.addEventListener("click", toggleChatFullscreen);

    document.getElementById("notificationsBtn")?.addEventListener("click", toggleNotifications);

    document.getElementById("langEnBtn")?.addEventListener("click", () => {
        setLanguage("en", applyTranslations);
    });

    document.getElementById("langRuBtn")?.addEventListener("click", () => {
        setLanguage("ru", applyTranslations);
    });

    document.getElementById("roomSearch")?.addEventListener("input", () => renderRooms({ onJoinRoom: joinRoom, onDeleteRoom: deleteRoom }));
    document.getElementById("creatorSearch")?.addEventListener("input", () => renderRooms({ onJoinRoom: joinRoom, onDeleteRoom: deleteRoom }));
    document.getElementById("onlineFilter")?.addEventListener("change", () => renderRooms({ onJoinRoom: joinRoom, onDeleteRoom: deleteRoom }));
    document.getElementById("sortRooms")?.addEventListener("change", () => renderRooms({ onJoinRoom: joinRoom, onDeleteRoom: deleteRoom }));

    document.getElementById("chat")?.addEventListener("scroll", handleChatScroll);

    window.addEventListener("scroll", closeMessageContextMenu, true);
    window.addEventListener("resize", closeMessageContextMenu);

    document.addEventListener("visibilitychange", () => {
        if (!document.hidden && state.token) {
            loadRooms();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMessageContextMenu();
        }
    });

    document.addEventListener("click", (event) => {
        const menu = document.getElementById("messageContextMenu");

        if (!menu || menu.classList.contains("hidden")) return;

        if (!menu.contains(event.target)) {
            closeMessageContextMenu();
        }
    });

    bindDragAndDrop();
    bindPasteUpload();
}

function bindDragAndDrop() {
    const chatElement = document.getElementById("chat");
    if (!chatElement) return;

    chatElement.addEventListener("dragover", (event) => {
        event.preventDefault();

        if (!state.currentRoom) return;

        chatElement.classList.add("drag-over");
    });

    chatElement.addEventListener("dragleave", () => {
        chatElement.classList.remove("drag-over");
    });

    chatElement.addEventListener("drop", (event) => {
        event.preventDefault();

        chatElement.classList.remove("drag-over");

        if (!state.currentRoom || !state.currentRoomToken) return;

        const file = event.dataTransfer?.files?.[0];
        if (!file) return;

        setPendingAttachment(file);
    });
}

function bindPasteUpload() {
    document.addEventListener("paste", (event) => {
        if (!state.currentRoom || !state.currentRoomToken) return;

        const items = Array.from(event.clipboardData?.items || []);
        const fileItem = items.find(item => item.kind === "file");

        if (!fileItem) return;

        const file = fileItem.getAsFile();
        if (!file) return;

        event.preventDefault();

        const extension = file.type.startsWith("image/") ? "png" : "file";

        const namedFile = new File(
            [file],
            file.name || `pasted-${Date.now()}.${extension}`,
            { type: file.type }
        );

        setPendingAttachment(namedFile);
    });
}

bindEvents();
bindMessageActionEvents();
initializeSession();