import {
    createRoomRequest,
    deleteRoomRequest,
    joinRoomRequest,
    loadRoomsRequest,
} from "../api/rooms-api.js";
import { getApiErrorMessage } from "../i18n/api-errors.js";
import { t } from "../i18n/i18n.js";
import { connectWS } from "../realtime/websocket.js";
import { state } from "../state.js";
import {
    updateChatHeader,
    updateRoomsCount,
} from "../ui/header-ui.js";
import { renderRooms, setRoomsListCollapsed } from "../ui/rooms-ui.js";
import { setComposerStatus, setStatus } from "../ui/status.js";
import { logout } from "./auth.js";
import { clearChat, loadMessages, resetActiveRoomState } from "./chat.js";
import { refreshMentionUsers } from "./mentions.js";

export async function loadRooms() {
    try {
        const { res, data } = await loadRoomsRequest();

        if (!res.ok) {
            if (res.status === 401) {
                logout();
                setStatus("authStatus", t("sessionExpired"), true);
                return false;
            }

            setStatus("roomStatus", getApiErrorMessage(data, "cannotLoadRooms"), true);
            return false;
        }

        state.allRooms = data;

        updateRoomsCount();
        renderRooms({
            onJoinRoom: joinRoom,
            onDeleteRoom: deleteRoom
        });

        return true;
    } catch {
        setStatus("roomStatus", t("cannotLoadRooms"), true);
        return false;
    }
}

export function startRoomsAutoRefresh() {
    stopRoomsAutoRefresh();

    state.roomsRefreshTimer = setInterval(() => {
        if (!state.token || document.hidden) return;
        loadRooms();
    }, 10000);
}

export function stopRoomsAutoRefresh() {
    if (state.roomsRefreshTimer) {
        clearInterval(state.roomsRefreshTimer);
        state.roomsRefreshTimer = null;
    }
}

export async function createRoom() {
    const name = document.getElementById("newRoomName").value.trim();
    const password = document.getElementById("newRoomPassword").value.trim();

    if (!name || !password) {
        setStatus("roomStatus", t("fillRoomData"), true);
        return;
    }

    const { res, data } = await createRoomRequest(name, password);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotCreateRoom"), true);
        return;
    }

    setStatus("roomStatus", t("roomCreated", { room: name }));

    document.getElementById("newRoomName").value = "";
    document.getElementById("newRoomPassword").value = "";

    await loadRooms();
}

export async function joinRoom(roomName, passwordInput) {
    const password = passwordInput ? passwordInput.value.trim() : "";

    if (!password && !state.currentIsAdmin) {
        setStatus("roomStatus", t("enterRoomPassword"), true);
        return;
    }

    const { res, data } = await joinRoomRequest(roomName, password);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotJoinRoom"), true);
        return;
    }

    state.currentRoom = roomName;
    state.currentRoomToken = data.room_token;

    updateChatHeader();

    document.getElementById("leaveChatBtn").classList.remove("hidden");
    document.getElementById("roomUsersBtn").classList.remove("hidden");

    state.messagesNextBeforeId = null;
    state.messagesHasMore = true;
    state.messagesLoading = false;

    clearChat();

    await loadMessages();
    await refreshMentionUsers();

    connectWS();

    setRoomsListCollapsed(true);
    setStatus("roomStatus", t("joinedRoom", { room: roomName }));
    setComposerStatus("");

    await loadRooms();
}

export async function deleteRoom(roomName) {
    if (!confirm(t("confirmDeleteRoom", { room: roomName }))) {
        return;
    }

    const { res, data } = await deleteRoomRequest(roomName);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotDeleteRoom"), true);
        return;
    }

    if (roomName === state.currentRoom) {
        resetActiveRoomState();
    }

    setStatus("roomStatus", t("deletedRoom", { room: roomName }));
    await loadRooms();
}

export async function leaveChat() {
    resetActiveRoomState();
    setStatus("roomStatus", t("leftRoom"));
    await loadRooms();
}