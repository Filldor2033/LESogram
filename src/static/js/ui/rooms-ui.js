import { deleteRoom, joinRoom } from "../features/rooms.js";
import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

export function setRoomsListCollapsed(collapsed) {
    state.roomsListCollapsed = collapsed;

    const roomsListSection = document.getElementById("roomsListSection");
    const toggleButton = document.getElementById("toggleRoomsBtn");

    roomsListSection.classList.toggle("hidden", collapsed);
    toggleButton.textContent = collapsed ? t("showList") : t("hideList");
}

export function toggleRoomsList() {
    setRoomsListCollapsed(!state.roomsListCollapsed);
}

export function getFilteredRooms() {
    const roomSearch = document.getElementById("roomSearch")?.value.trim().toLowerCase() || "";
    const creatorSearch = document.getElementById("creatorSearch")?.value.trim().toLowerCase() || "";
    const onlineFilter = document.getElementById("onlineFilter")?.value || "all";
    const sortMode = document.getElementById("sortRooms")?.value || "name_asc";

    let rooms = [...state.allRooms];

    if (roomSearch) {
        rooms = rooms.filter(room => room.name.toLowerCase().includes(roomSearch));
    }

    if (creatorSearch) {
        rooms = rooms.filter(room =>
            String(room.created_by).toLowerCase().includes(creatorSearch)
        );
    }

    if (onlineFilter === "online") {
        rooms = rooms.filter(room => Number(room.online) > 0);
    }

    if (onlineFilter === "empty") {
        rooms = rooms.filter(room => Number(room.online) === 0);
    }

    rooms.sort((a, b) => {
        if (sortMode === "name_asc") return a.name.localeCompare(b.name);
        if (sortMode === "name_desc") return b.name.localeCompare(a.name);
        if (sortMode === "online_desc") return Number(b.online) - Number(a.online);
        if (sortMode === "online_asc") return Number(a.online) - Number(b.online);
        if (sortMode === "creator_asc") return String(a.created_by).localeCompare(String(b.created_by));

        return 0;
    });

    return rooms;
}

export function renderRooms({ onJoinRoom, onDeleteRoom }) {
    const list = document.getElementById("roomsList");
    list.innerHTML = "";

    const rooms = getFilteredRooms();

    if (!state.allRooms.length) {
        const empty = document.createElement("div");
        empty.className = "status";
        empty.textContent = t("roomsNone");
        list.appendChild(empty);
        return;
    }

    if (!rooms.length) {
        const empty = document.createElement("div");
        empty.className = "status";
        empty.textContent = t("roomsNotFound");
        list.appendChild(empty);
        return;
    }

    for (const room of rooms) {
        const item = document.createElement("div");
        item.className = "room-item";

        const title = document.createElement("div");
        title.className = "room-title";
        title.textContent = room.name;

        const meta = document.createElement("div");
        meta.className = "room-meta";

        const creatorLine = document.createElement("div");
        creatorLine.textContent = `${t("creatorLabel")}: ${room.created_by}`;

        const onlineLine = document.createElement("div");
        onlineLine.textContent = `${t("onlineLabel")}: ${room.online}`;

        const input = document.createElement("input");
        input.type = "password";
        input.placeholder = t("roomPasswordPlaceholder");

        if (state.currentIsAdmin) {
            input.placeholder = "";
            input.required = false;
        }

        const button = document.createElement("button");
        button.textContent = t("join");
        button.addEventListener("click", () => onJoinRoom(room.name, input));

        const actions = document.createElement("div");
        actions.className = "room-actions";
        actions.appendChild(button);

        if (room.created_by === state.currentUser || state.currentIsAdmin) {
            const deleteButton = document.createElement("button");
            deleteButton.className = "danger";
            deleteButton.textContent = t("delete");
            deleteButton.addEventListener("click", () => onDeleteRoom(room.name));
            actions.appendChild(deleteButton);
        }

        meta.appendChild(creatorLine);
        meta.appendChild(onlineLine);

        item.appendChild(title);
        item.appendChild(meta);

        if (!state.currentIsAdmin) {
            item.appendChild(input);
        }

        item.appendChild(actions);
        list.appendChild(item);
    }
}

export function resetRoomFilters() {
    document.getElementById("roomSearch").value = "";
    document.getElementById("creatorSearch").value = "";
    document.getElementById("onlineFilter").value = "all";
    document.getElementById("sortRooms").value = "name_asc";

    renderRooms({
        onJoinRoom: joinRoom,
        onDeleteRoom: deleteRoom
    });
}