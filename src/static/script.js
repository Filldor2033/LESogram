const translations = {
    en: {
        users: "Users",
        onlineUsers: "Online users",
        noOnlineUsers: "No users online",
        close: "Close",
        appTitle: "LESogram",
        brandSubtitle: "Fast rooms, live messages, simple sharing",
        authTitle: "Account",
        usernamePlaceholder: "Username",
        passwordPlaceholder: "Password",
        login: "Login",
        register: "Register",
        logout: "Exit",
        adminBadge: "Admin",
        youBadge: "you",
        onlineBadge: "online",
        createRoomTitle: "Create Room",
        newRoomNamePlaceholder: "New room name",
        roomPasswordPlaceholder: "Room password",
        createRoom: "Create room",
        roomListTitle: "Room List",
        roomListSubtitle: "Browse and join",
        hideList: "Hide list",
        showList: "Show list",
        roomSearchPlaceholder: "Search by room name...",
        creatorSearchPlaceholder: "Search by creator...",
        allRooms: "All rooms",
        onlineOnly: "Only with online users",
        emptyOnly: "Only empty rooms",
        sortNameAsc: "Name A-Z",
        sortNameDesc: "Name Z-A",
        sortOnlineDesc: "Online first",
        sortOnlineAsc: "Online last",
        sortCreatorAsc: "Creator A-Z",
        refreshRooms: "Refresh rooms",
        resetFilters: "Reset filters",
        chatNotSelected: "Chat not selected",
        chooseRoom: "Choose a room to start chatting",
        roomHeader: "Room: {room}",
        realtimeActive: "Realtime conversation is active",
        leaveChat: "Exit chat",
        pickMedia: "Photo or video",
        pickFile: "File",
        messagePlaceholder: "Type a message or add a caption...",
        send: "Send",
        emptyNoRoomTitle: "No room selected yet",
        emptyNoRoomText: "Pick a room on the left to open the conversation, send text, and share photos, videos, or files.",
        emptyNoMessagesTitle: "No messages yet",
        emptyNoMessagesText: "Start the conversation with a text message or share media.",
        roomsNone: "No rooms yet",
        roomsNotFound: "No rooms found",
        creatorLabel: "creator",
        onlineLabel: "online",
        join: "Join",
        delete: "Delete",
        download: "Download",
        attachmentLabel: "Attachment",
        fileLabel: "File",
        roomCount_one: "{count} room",
        roomCount_many: "{count} rooms",
        authFill: "Fill username and password",
        authFailed: "Auth failed",
        sessionExpired: "Session expired. Please login again.",
        cannotLoadRooms: "Cannot load rooms",
        fillRoomData: "Fill room name and password",
        roomCreated: "Room \"{room}\" created",
        cannotCreateRoom: "Cannot create room",
        cannotDeleteRoom: "Cannot delete room",
        enterRoomPassword: "Enter room password",
        cannotJoinRoom: "Cannot join room",
        joinedRoom: "Joined room \"{room}\"",
        deletedRoom: "Room \"{room}\" deleted",
        roomDeletedByOwner: "Room \"{room}\" was deleted by its creator",
        confirmDeleteRoom: "Delete room \"{room}\"? This will remove its messages and files for everyone.",
        cannotLoadMessages: "Cannot load messages",
        realtimeClosed: "Realtime connection closed",
        joinRoomFirst: "Join a room first",
        realtimeNotReady: "Realtime connection is not ready",
        uploadingFile: "Uploading {file}...",
        fileSent: "{file} sent",
        uploadFailed: "Upload failed",
        leftRoom: "You left the room",
        systemJoined: "{user} joined",
        systemLeft: "{user} left",
        systemRoomDeleted: "Room was deleted by {user}",
        systemRateLimited: "Too many actions. Please slow down.",
        apiMissingToken: "Missing token",
        apiInvalidToken: "Invalid token",
        apiUserExists: "User already exists",
        apiInvalidCredentials: "Invalid credentials",
        apiRoomExists: "Room already exists",
        apiRoomNotFound: "Room not found",
        apiWrongRoomPassword: "Wrong room password",
        apiNoRoomAccess: "No access to this room",
        apiDeleteDenied: "Only the creator can delete this room",
        apiAttachmentMissingName: "Attachment is missing a file name",
        apiAttachmentNotFound: "Attachment not found",
        apiFileTypeNotAllowed: "File type is not allowed",
        apiGifDisabled: "GIF uploads are disabled",
        apiAttachmentEmpty: "Attachment is empty",
        apiAttachmentTooLarge: "Attachment is too large. Max size is {size} MB",
        apiMessageTooLong: "Message must be at most {max} characters",
        apiMessageEmpty: "Message cannot be empty",
        apiTooManyRequests: "Too many requests. Retry in {seconds} seconds"
    },
    ru: {
        users: "Участники",
        onlineUsers: "Пользователи онлайн",
        noOnlineUsers: "Нет пользователей онлайн",
        close: "Закрыть",
        appTitle: "LESogram",
        brandSubtitle: "Быстрые комнаты, живые сообщения и удобная отправка файлов",
        authTitle: "Аккаунт",
        usernamePlaceholder: "Имя пользователя",
        passwordPlaceholder: "Пароль",
        login: "Войти",
        register: "Регистрация",
        logout: "Выйти",
        adminBadge: "Админ",
        youBadge: "вы",
        onlineBadge: "онлайн",
        createRoomTitle: "Создать комнату",
        newRoomNamePlaceholder: "Название новой комнаты",
        roomPasswordPlaceholder: "Пароль комнаты",
        createRoom: "Создать комнату",
        roomListTitle: "Список комнат",
        roomListSubtitle: "Выберите и подключитесь",
        hideList: "Скрыть",
        showList: "Показать",
        roomSearchPlaceholder: "Поиск по названию комнаты...",
        creatorSearchPlaceholder: "Поиск по создателю...",
        allRooms: "Все комнаты",
        onlineOnly: "Только с пользователями онлайн",
        emptyOnly: "Только пустые комнаты",
        sortNameAsc: "Название А-Я",
        sortNameDesc: "Название Я-А",
        sortOnlineDesc: "Сначала онлайн",
        sortOnlineAsc: "Сначала пустые",
        sortCreatorAsc: "Создатель А-Я",
        refreshRooms: "Обновить комнаты",
        resetFilters: "Сбросить фильтры",
        chatNotSelected: "Чат не выбран",
        chooseRoom: "Выберите комнату, чтобы начать общение",
        roomHeader: "Комната: {room}",
        realtimeActive: "Чат подключён в реальном времени",
        leaveChat: "Выйти из чата",
        pickMedia: "Фото или видео",
        pickFile: "Файл",
        messagePlaceholder: "Введите сообщение или подпись...",
        send: "Отправить",
        emptyNoRoomTitle: "Комната пока не выбрана",
        emptyNoRoomText: "Выберите комнату слева, чтобы открыть переписку, отправлять текст, фото, видео и файлы.",
        emptyNoMessagesTitle: "Сообщений пока нет",
        emptyNoMessagesText: "Начните диалог с текста или отправьте медиа.",
        roomsNone: "Комнат пока нет",
        roomsNotFound: "Комнаты не найдены",
        creatorLabel: "создатель",
        onlineLabel: "онлайн",
        join: "Войти",
        delete: "Удалить",
        download: "Скачать",
        attachmentLabel: "Вложение",
        fileLabel: "Файл",
        roomCount_one: "{count} комната",
        roomCount_few: "{count} комнаты",
        roomCount_many: "{count} комнат",
        authFill: "Введите имя пользователя и пароль",
        authFailed: "Ошибка входа",
        sessionExpired: "Сессия истекла. Войдите снова.",
        cannotLoadRooms: "Не удалось загрузить комнаты",
        fillRoomData: "Введите название комнаты и пароль",
        roomCreated: "Комната \"{room}\" создана",
        cannotCreateRoom: "Не удалось создать комнату",
        cannotDeleteRoom: "Не удалось удалить комнату",
        enterRoomPassword: "Введите пароль комнаты",
        cannotJoinRoom: "Не удалось войти в комнату",
        joinedRoom: "Вы вошли в комнату \"{room}\"",
        deletedRoom: "Комната \"{room}\" удалена",
        roomDeletedByOwner: "Комната \"{room}\" была удалена создателем",
        confirmDeleteRoom: "Удалить комнату \"{room}\"? Для всех будут удалены сообщения и файлы.",
        cannotLoadMessages: "Не удалось загрузить сообщения",
        realtimeClosed: "Соединение в реальном времени закрыто",
        joinRoomFirst: "Сначала войдите в комнату",
        realtimeNotReady: "Соединение ещё не готово",
        uploadingFile: "Загрузка {file}...",
        fileSent: "{file} отправлен",
        uploadFailed: "Не удалось загрузить файл",
        leftRoom: "Вы вышли из комнаты",
        systemJoined: "{user} вошёл(а)",
        systemLeft: "{user} вышел(а)",
        systemRoomDeleted: "Комната удалена пользователем {user}",
        systemRateLimited: "Слишком много действий. Немного подождите.",
        apiMissingToken: "Токен отсутствует",
        apiInvalidToken: "Недействительный токен",
        apiUserExists: "Пользователь уже существует",
        apiInvalidCredentials: "Неверные данные для входа",
        apiRoomExists: "Комната уже существует",
        apiRoomNotFound: "Комната не найдена",
        apiWrongRoomPassword: "Неверный пароль комнаты",
        apiNoRoomAccess: "Нет доступа к этой комнате",
        apiDeleteDenied: "Удалять комнату может только её создатель",
        apiAttachmentMissingName: "У файла отсутствует имя",
        apiAttachmentNotFound: "Вложение не найдено",
        apiFileTypeNotAllowed: "Такой тип файла запрещён",
        apiGifDisabled: "Загрузка GIF отключена",
        apiAttachmentEmpty: "Файл пустой",
        apiAttachmentTooLarge: "Файл слишком большой. Максимум {size} МБ",
        apiMessageTooLong: "Сообщение должно быть не длиннее {max} символов",
        apiMessageEmpty: "Сообщение не может быть пустым",
        apiTooManyRequests: "Слишком много запросов. Повторите через {seconds} сек."
    }
};

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
    "Message cannot be empty": "apiMessageEmpty"
};

let token = localStorage.getItem("token") || "";
let currentUser = localStorage.getItem("username") || "";
let currentRoom = "";
let currentRoomToken = "";
let ws = null;
let roomsListCollapsed = false;
let allRooms = [];
let currentLanguage = getInitialLanguage();
let suppressNextWsCloseStatus = false;
let roomsRefreshTimer = null;
let currentIsAdmin = localStorage.getItem("is_admin") === "1";
let messagesNextBeforeId = null;
let messagesHasMore = true;
let messagesLoading = false;

async function loadMe() {
    const res = await fetch("/me", {
        headers: authHeaders({ json: false })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        if (res.status === 401) {
            logout();
        }
        return false;
    }

    currentUser = data.username;
    currentIsAdmin = Boolean(data.is_admin);

    localStorage.setItem("username", currentUser);
    localStorage.setItem("is_admin", currentIsAdmin ? "1" : "0");

    return true;
}

function getInitialLanguage() {
    const saved = localStorage.getItem("language");
    if (saved === "en" || saved === "ru") {
        return saved;
    }
    return navigator.language && navigator.language.toLowerCase().startsWith("ru") ? "ru" : "en";
}

function t(key, vars = {}) {
    const source = translations[currentLanguage][key] ?? translations.en[key] ?? key;
    return source.replace(/\{(\w+)\}/g, (_, name) => String(vars[name] ?? `{${name}}`));
}

function pluralizeRu(count, one, few, many) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) return one;
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
    return many;
}

function formatRoomCount(count) {
    if (currentLanguage === "ru") {
        const form = pluralizeRu(count, t("roomCount_one", { count }), t("roomCount_few", { count }), t("roomCount_many", { count }));
        return form;
    }
    return count === 1 ? t("roomCount_one", { count }) : t("roomCount_many", { count });
}

function scrollChatToBottom() {
    const chat = document.getElementById("chat");
    if (!chat) return;

    requestAnimationFrame(() => {
        chat.scrollTop = chat.scrollHeight;
    });
}

function translateApiDetail(detail) {
    if (!detail) return "";
    if (typeof detail !== "string") return "";

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

function getApiErrorMessage(data, fallbackKey) {
    const translated = translateApiDetail(data?.detail);
    return translated || t(fallbackKey);
}

function setLanguage(language) {
    if (!translations[language]) return;
    currentLanguage = language;
    localStorage.setItem("language", language);
    applyTranslations();
}

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

function updateTopAdminBadge() {
    const badge = document.getElementById("adminTopBadge");
    if (!badge) return;

    badge.textContent = `👑 ${t("adminBadge")}`;
    badge.classList.toggle("hidden", !currentIsAdmin);
}

function updateLanguageButtons() {
    document.getElementById("langEnBtn").classList.toggle("active", currentLanguage === "en");
    document.getElementById("langRuBtn").classList.toggle("active", currentLanguage === "ru");
}

function updateRoomsCount() {
    const pill = document.getElementById("roomsCountPill");
    if (!pill) return;
    pill.textContent = formatRoomCount(allRooms.length);
}

function updateChatHeader() {
    document.getElementById("chatHeader").innerText = currentRoom ? t("roomHeader", { room: currentRoom }) : t("chatNotSelected");
    document.getElementById("chatSubheader").innerText = currentRoom ? t("realtimeActive") : t("chooseRoom");
}

function renderChatEmptyState() {
    const chat = document.getElementById("chat");
    let empty = document.getElementById("chatEmptyState");

    if (!empty) {
        empty = document.createElement("div");
        empty.id = "chatEmptyState";
        empty.className = "chat-empty";
    }

    empty.innerHTML = `
        <div class="chat-empty-title">${currentRoom ? t("emptyNoMessagesTitle") : t("emptyNoRoomTitle")}</div>
        <div class="chat-empty-text">${currentRoom ? t("emptyNoMessagesText") : t("emptyNoRoomText")}</div>
    `;

    chat.appendChild(empty);
}

function toggleChatEmptyState() {
    const empty = document.getElementById("chatEmptyState");
    const chat = document.getElementById("chat");
    if (!empty || !chat) return;

    const hasRealMessages = Array.from(chat.children).some(node => node.id !== "chatEmptyState");
    empty.classList.toggle("hidden", hasRealMessages);
}

function refreshRuntimeTranslations() {
    document.querySelectorAll(".system[data-system-event][data-system-actor]").forEach((node) => {
        const event = node.dataset.systemEvent;
        const actor = node.dataset.systemActor;
        const key = event === "joined" ? "systemJoined" : "systemLeft";
        node.textContent = t(key, { user: actor });
    });

    document.querySelectorAll(".file-link[data-i18n-key='download']").forEach((node) => {
        node.textContent = t("download");
    });
}

function applyTranslations() {
    document.documentElement.lang = currentLanguage;
    document.title = t("appTitle");

    document.getElementById("brandSubtitle").textContent = t("brandSubtitle");
    document.getElementById("authTitle").textContent = t("authTitle");
    document.getElementById("createRoomTitle").textContent = t("createRoomTitle");
    document.getElementById("roomListTitle").textContent = t("roomListTitle");
    document.getElementById("roomListSubtitle").textContent = t("roomListSubtitle");

    setButtonText("loginBtn", "login");
    setButtonText("registerBtn", "register");
    setButtonText("logoutBtn", "logout");
    setButtonText("createRoomBtn", "createRoom");
    setButtonText("refreshRoomsBtn", "refreshRooms");
    setButtonText("resetFiltersBtn", "resetFilters");
    setButtonText("leaveChatBtn", "leaveChat");
    setButtonText("pickMediaBtn", "pickMedia");
    setButtonText("pickFileBtn", "pickFile");
    setButtonText("sendBtn", "send");

    setInputPlaceholder("username", "usernamePlaceholder");
    setInputPlaceholder("password", "passwordPlaceholder");
    setInputPlaceholder("newRoomName", "newRoomNamePlaceholder");
    setInputPlaceholder("newRoomPassword", "roomPasswordPlaceholder");
    setInputPlaceholder("roomSearch", "roomSearchPlaceholder");
    setInputPlaceholder("creatorSearch", "creatorSearchPlaceholder");
    setInputPlaceholder("message", "messagePlaceholder");

    document.getElementById("onlineFilterAll").textContent = t("allRooms");
    document.getElementById("onlineFilterOnline").textContent = t("onlineOnly");
    document.getElementById("onlineFilterEmpty").textContent = t("emptyOnly");
    document.getElementById("sortNameAsc").textContent = t("sortNameAsc");
    document.getElementById("sortNameDesc").textContent = t("sortNameDesc");
    document.getElementById("sortOnlineDesc").textContent = t("sortOnlineDesc");
    document.getElementById("sortOnlineAsc").textContent = t("sortOnlineAsc");
    document.getElementById("sortCreatorAsc").textContent = t("sortCreatorAsc");

    setButtonText("roomUsersBtn", "users");
    const usersTitle = document.getElementById("usersPopupTitle");
    if (usersTitle) {
        usersTitle.textContent = t("onlineUsers");
    }

    updateLanguageButtons();
    updateChatHeader();
    updateRoomsCount();
    updateTopAdminBadge();
    renderChatEmptyState();
    toggleChatEmptyState();
    refreshRuntimeTranslations();
    setRoomsListCollapsed(roomsListCollapsed);
    renderRooms();
}

function setStatus(id, text, isError = false) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text || "";
    el.className = "status" + (isError ? " error" : "");
}

function setComposerStatus(text, isError = false) {
    setStatus("composerStatus", text, isError);
}

function authHeaders(options = {}) {
    const headers = {
        "Authorization": "Bearer " + token
    };

    if (options.json !== false) {
        headers["Content-Type"] = "application/json";
    }

    return headers;
}

function formatTime(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    const locale = currentLanguage === "ru" ? "ru-RU" : "en-US";
    return d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
}

function formatBytes(bytes) {
    const size = Number(bytes || 0);
    if (!size) return "";

    const units = ["B", "KB", "MB", "GB"];
    let value = size;
    let unit = units[0];

    for (let i = 0; i < units.length; i++) {
        unit = units[i];
        if (value < 1024 || i === units.length - 1) break;
        value /= 1024;
    }

    return `${value >= 10 ? value.toFixed(0) : value.toFixed(1)} ${unit}`;
}

function resolveAttachmentUrl(mediaUrl) {
    if (!mediaUrl) {
        return "";
    }

    if (!currentRoomToken) {
        return mediaUrl;
    }

    const separator = mediaUrl.includes("?") ? "&" : "?";
    return `${mediaUrl}${separator}room_token=${encodeURIComponent(currentRoomToken)}`;
}

function getMessageType(payload) {
    return payload.content_type || "text";
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

function getSystemMessageText(payload) {
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

function createMessageNode(payload) {
    const div = document.createElement("div");

    if (payload.id) {
        div.dataset.messageId = String(payload.id);
    }

    if (payload.type === "system") {
        div.className = "msg system";
        if (payload.system_event) div.dataset.systemEvent = payload.system_event;
        if (payload.system_actor) div.dataset.systemActor = payload.system_actor;
        div.innerText = getSystemMessageText(payload);
        return div;
    }

    const mine = payload.username === currentUser;
    div.className = "msg " + (mine ? "me" : "other");

    const username = document.createElement("div");
    username.className = "msg-username";
    username.textContent = payload.username;

    const attachmentNode = buildAttachmentNode(payload);
    const hasText = Boolean((payload.text || "").trim());

    div.appendChild(username);

    if (attachmentNode) div.appendChild(attachmentNode);

    if (hasText) {
        const text = document.createElement("div");
        text.className = "msg-text";
        text.textContent = payload.text;
        div.appendChild(text);
    }

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.innerText = formatTime(payload.timestamp);
    div.appendChild(meta);

    return div;
}

function addMessage(payload) {
    const chat = document.getElementById("chat");
    const div = createMessageNode(payload);

    chat.appendChild(div);
    toggleChatEmptyState();
    scrollChatToBottom();
}

async function deleteMessage(messageId) {
    if (!currentIsAdmin) return;

    const res = await fetch(`/messages/${encodeURIComponent(messageId)}`, {
        method: "DELETE",
        headers: authHeaders({ json: false })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        setComposerStatus(getApiErrorMessage(data, "cannotDeleteRoom"), true);
        return;
    }

    removeMessageFromChat(messageId);
}

function removeMessageFromChat(messageId) {
    document.querySelectorAll(".msg[data-message-id]").forEach((node) => {
        if (node.dataset.messageId === String(messageId)) {
            node.remove();
        }
    });

    toggleChatEmptyState();
}

function clearChat() {
    document.getElementById("chat").innerHTML = "";
    renderChatEmptyState();
    toggleChatEmptyState();
}

function setRoomsListCollapsed(collapsed) {
    roomsListCollapsed = collapsed;

    const roomsListSection = document.getElementById("roomsListSection");
    const toggleButton = document.getElementById("toggleRoomsBtn");

    roomsListSection.classList.toggle("hidden", collapsed);
    toggleButton.textContent = collapsed ? t("showList") : t("hideList");
}

function toggleRoomsList() {
    setRoomsListCollapsed(!roomsListCollapsed);
}

function showLoggedInState() {
    document.getElementById("authSection").classList.add("hidden");
    document.getElementById("roomsSection").classList.remove("hidden");
    document.getElementById("whoami").innerText = currentUser;

    updateTopAdminBadge();
}

function showLoggedOutState() {
    document.getElementById("authSection").classList.remove("hidden");
    document.getElementById("roomsSection").classList.add("hidden");
}

async function safeJson(res) {
    try {
        return await res.json();
    } catch {
        return {};
    }
}

function startRoomsAutoRefresh() {
    stopRoomsAutoRefresh();

    roomsRefreshTimer = setInterval(() => {
        if (!token || document.hidden) return;
        loadRooms();
    }, 10000);
}

function stopRoomsAutoRefresh() {
    if (roomsRefreshTimer) {
        clearInterval(roomsRefreshTimer);
        roomsRefreshTimer = null;
    }
}

async function auth(mode) {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        setStatus("authStatus", t("authFill"), true);
        return;
    }

    const res = await fetch(`/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        setStatus("authStatus", getApiErrorMessage(data, "authFailed"), true);
        return;
    }

    token = data.access_token;
    currentUser = username;

    localStorage.setItem("token", token);
    localStorage.setItem("username", username);

    await loadMe();

    showLoggedInState();
    setStatus("authStatus", "");
    await loadRooms();
    startRoomsAutoRefresh();
}

async function loadRooms() {
    try {
        const res = await fetch("/rooms", {
            headers: authHeaders({ json: false })
        });

        const data = await safeJson(res);

        if (!res.ok) {
            if (res.status === 401) {
                logout();
                setStatus("authStatus", t("sessionExpired"), true);
                return false;
            }

            setStatus("roomStatus", getApiErrorMessage(data, "cannotLoadRooms"), true);
            return false;
        }

        allRooms = data;
        updateRoomsCount();
        renderRooms();
        return true;
    } catch {
        setStatus("roomStatus", t("cannotLoadRooms"), true);
        return false;
    }
}

function getFilteredRooms() {
    const roomSearch = document.getElementById("roomSearch")?.value.trim().toLowerCase() || "";
    const creatorSearch = document.getElementById("creatorSearch")?.value.trim().toLowerCase() || "";
    const onlineFilter = document.getElementById("onlineFilter")?.value || "all";
    const sortMode = document.getElementById("sortRooms")?.value || "name_asc";

    let rooms = [...allRooms];

    if (roomSearch) {
        rooms = rooms.filter(room => room.name.toLowerCase().includes(roomSearch));
    }

    if (creatorSearch) {
        rooms = rooms.filter(room => String(room.created_by).toLowerCase().includes(creatorSearch));
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

function renderRooms() {
    const list = document.getElementById("roomsList");
    list.innerHTML = "";

    const rooms = getFilteredRooms();

    if (!allRooms.length) {
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

        if (currentIsAdmin) {
            input.placeholder = "";
            input.required = false;
        }

        const button = document.createElement("button");
        button.textContent = t("join");
        button.addEventListener("click", () => joinRoom(room.name, input));

        const actions = document.createElement("div");
        actions.className = "room-actions";
        actions.appendChild(button);

        if (room.created_by === currentUser || currentIsAdmin) {
            const deleteButton = document.createElement("button");
            deleteButton.className = "danger";
            deleteButton.textContent = t("delete");
            deleteButton.addEventListener("click", () => deleteRoom(room.name));
            actions.appendChild(deleteButton);
        }

        meta.appendChild(creatorLine);
        meta.appendChild(onlineLine);

        item.appendChild(title);
        item.appendChild(meta);
        if (!currentIsAdmin) {
            item.appendChild(input);
        }
        item.appendChild(actions);

        list.appendChild(item);
    }
}

function resetRoomFilters() {
    document.getElementById("roomSearch").value = "";
    document.getElementById("creatorSearch").value = "";
    document.getElementById("onlineFilter").value = "all";
    document.getElementById("sortRooms").value = "name_asc";
    renderRooms();
}

async function createRoom() {
    const name = document.getElementById("newRoomName").value.trim();
    const password = document.getElementById("newRoomPassword").value.trim();

    if (!name || !password) {
        setStatus("roomStatus", t("fillRoomData"), true);
        return;
    }

    const res = await fetch("/rooms", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ name, password })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotCreateRoom"), true);
        return;
    }

    setStatus("roomStatus", t("roomCreated", { room: name }));
    document.getElementById("newRoomName").value = "";
    document.getElementById("newRoomPassword").value = "";
    await loadRooms();
}

async function joinRoom(roomName, pwdInput) {
    const password = pwdInput ? pwdInput.value.trim() : "";

    if (!password && !currentIsAdmin) {
        setStatus("roomStatus", t("enterRoomPassword"), true);
        return;
    }

    const res = await fetch("/rooms/join", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
            room: roomName,
            password: password
        })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotJoinRoom"), true);
        return;
    }

    currentRoom = roomName;
    currentRoomToken = data.room_token;
    updateChatHeader();
    document.getElementById("leaveChatBtn").classList.remove("hidden");
    document.getElementById("roomUsersBtn").classList.remove("hidden");

    messagesNextBeforeId = null;
    messagesHasMore = true;
    messagesLoading = false;

    clearChat();
    await loadMessages();
    connectWS();

    setRoomsListCollapsed(true);
    setStatus("roomStatus", t("joinedRoom", { room: roomName }));
    setComposerStatus("");

    await loadRooms();
}

async function loadMessages({ older = false } = {}) {
    if (messagesLoading) return;

    messagesLoading = true;

    const chat = document.getElementById("chat");
    const oldScrollHeight = chat.scrollHeight;
    const oldScrollTop = chat.scrollTop;

    try {
        let url = `/messages/${encodeURIComponent(currentRoom)}?room_token=${encodeURIComponent(currentRoomToken)}`;

        if (older && messagesNextBeforeId) {
            url += `&before_id=${encodeURIComponent(messagesNextBeforeId)}`;
        }

        const res = await fetch(url);
        const data = await safeJson(res);

        if (!res.ok) {
            setStatus("roomStatus", getApiErrorMessage(data, "cannotLoadMessages"), true);
            return;
        }

        const messages = data.messages || [];

        messagesNextBeforeId = data.next_before_id;
        messagesHasMore = Boolean(data.has_more);

        if (older) {
            const fragment = document.createDocumentFragment();

            for (const message of messages) {
                fragment.appendChild(createMessageNode(message));
            }

            chat.insertBefore(fragment, chat.firstChild);
            toggleChatEmptyState();
        } else {
            for (const message of messages) {
                addMessage(message);
            }
        }

        if (older) {
            const newScrollHeight = chat.scrollHeight;
            chat.scrollTop = newScrollHeight - oldScrollHeight + oldScrollTop;
        } else {
            scrollChatToBottom();
        }
    } catch {
        setStatus("roomStatus", t("cannotLoadMessages"), true);
    } finally {
        messagesLoading = false;
    }
}

function connectWS() {
    if (ws) {
        suppressNextWsCloseStatus = true;
        ws.close();
    }

    const roomAtConnect = currentRoom;
    const tokenAtConnect = currentRoomToken;

    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
        `${protocol}://${location.host}/ws/${encodeURIComponent(roomAtConnect)}?room_token=${encodeURIComponent(tokenAtConnect)}`
    );

    ws = socket;

    socket.onmessage = (event) => {
        if (socket !== ws) return;
        if (roomAtConnect !== currentRoom) return;

        let payload;
        try {
            payload = JSON.parse(event.data);
        } catch {
            return;
        }

        if (payload.room && payload.room !== currentRoom) return;

        if (
            payload.type === "system" &&
            payload.system_event === "room_deleted" &&
            payload.room === currentRoom
        ) {
            handleRoomDeleted(payload);
            return;
        }

        if (payload.type === "message_deleted") {
            removeMessageFromChat(payload.message_id);
            return;
        }

        addMessage(payload);
        if (!document.getElementById("usersPopup")?.classList.contains("hidden")) {
            loadRoomUsers();
        }
    };

    socket.onclose = () => {
        if (socket !== ws) return;

        if (suppressNextWsCloseStatus) {
            suppressNextWsCloseStatus = false;
            return;
        }

        if (currentRoom) {
            setComposerStatus(t("realtimeClosed"), true);
        }
    };

    socket.onopen = () => {
        if (socket !== ws) return;
        setComposerStatus("");
    };
}

function ensureRoomSelected() {
    if (!currentRoom || !currentRoomToken) {
        setComposerStatus(t("joinRoomFirst"), true);
        return false;
    }
    return true;
}

function handleComposerKey(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    if (!ensureRoomSelected()) return;

    const input = document.getElementById("message");
    const text = input.value.trim();

    if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            setComposerStatus(t("realtimeNotReady"), true);
        }
        return;
    }

    ws.send(JSON.stringify({ text }));
    input.value = "";
    setComposerStatus("");
}

function pickMedia() {
    if (!ensureRoomSelected()) return;
    document.getElementById("mediaInput").click();
}

function pickFile() {
    if (!ensureRoomSelected()) return;
    document.getElementById("fileInput").click();
}

function shouldAppendHttpResponse() {
    return !ws || ws.readyState !== WebSocket.OPEN;
}

async function deleteRoom(roomName) {
    if (!confirm(t("confirmDeleteRoom", { room: roomName }))) {
        return;
    }

    const res = await fetch(`/rooms/${encodeURIComponent(roomName)}`, {
        method: "DELETE",
        headers: authHeaders({ json: false })
    });

    const data = await safeJson(res);

    if (!res.ok) {
        setStatus("roomStatus", getApiErrorMessage(data, "cannotDeleteRoom"), true);
        return;
    }

    if (roomName === currentRoom) {
        resetActiveRoomState();
    }

    setStatus("roomStatus", t("deletedRoom", { room: roomName }));
    await loadRooms();
}

async function loadRoomUsers() {
    if (!currentRoom || !currentRoomToken) return;

    const list = document.getElementById("usersList");
    const subtitle = document.getElementById("usersPopupSubtitle");

    if (!list || !subtitle) return;

    list.innerHTML = `<div class="users-loading">...</div>`;

    try {
        const res = await fetch(
            `/rooms/${encodeURIComponent(currentRoom)}/users?room_token=${encodeURIComponent(currentRoomToken)}`
        );

        const data = await safeJson(res);

        if (!res.ok) {
            list.innerHTML = `<div class="users-empty">${getApiErrorMessage(data, "cannotLoadRooms")}</div>`;
            subtitle.textContent = formatRoomCount(0);
            return;
        }

        subtitle.textContent = formatRoomCount(data.count || 0);
        renderUsersList(data.users || []);
    } catch {
        list.innerHTML = `<div class="users-empty">${t("cannotLoadRooms")}</div>`;
        subtitle.textContent = formatRoomCount(0);
    }
}

function renderUsersList(users) {
    const list = document.getElementById("usersList");
    if (!list) return;

    list.innerHTML = "";

    if (!users.length) {
        const empty = document.createElement("div");
        empty.className = "users-empty";
        empty.textContent = t("noOnlineUsers");
        list.appendChild(empty);
        return;
    }

    for (const user of users) {
        const username = typeof user === "string" ? user : user.username;
        const isAdmin = typeof user === "object" && Boolean(user.is_admin);

        const item = document.createElement("div");
        item.className = "user-item";

        const avatar = document.createElement("div");
        avatar.className = "user-avatar";
        avatar.textContent = username.slice(0, 1).toUpperCase();

        const name = document.createElement("div");
        name.className = "user-name";
        name.textContent = username;

        const badges = document.createElement("div");
        badges.className = "user-badges";

        if (isAdmin) {
            const adminBadge = document.createElement("div");
            adminBadge.className = "user-admin-badge";
            adminBadge.textContent = `👑 ${t("adminBadge")}`;
            badges.appendChild(adminBadge);
        }

        const statusBadge = document.createElement("div");
        statusBadge.className = "user-badge";
        statusBadge.textContent = username === currentUser ? t("youBadge") : t("onlineBadge");
        badges.appendChild(statusBadge);

        item.appendChild(avatar);
        item.appendChild(name);
        item.appendChild(badges);

        list.appendChild(item);
    }
}

function toggleUsersPopup() {
    const popup = document.getElementById("usersPopup");
    if (!popup) return;

    const willOpen = popup.classList.contains("hidden");

    if (willOpen) {
        popup.classList.remove("hidden");
        loadRoomUsers();
    } else {
        popup.classList.add("hidden");
    }
}

function closeUsersPopup() {
    const popup = document.getElementById("usersPopup");
    if (popup) {
        popup.classList.add("hidden");
    }
}

function resetActiveRoomState() {
    if (ws) {
        suppressNextWsCloseStatus = true;
        ws.close();
        ws = null;
    }

    currentRoom = "";
    currentRoomToken = "";

    updateChatHeader();
    document.getElementById("leaveChatBtn").classList.add("hidden");
    document.getElementById("roomUsersBtn").classList.add("hidden");
    closeUsersPopup();
    document.getElementById("message").value = "";
    clearChat();
    setRoomsListCollapsed(false);
    setComposerStatus("");
}

async function handleRoomDeleted(payload) {
    const deletedRoom = payload.room || currentRoom;
    const actor = payload.system_actor || "";
    const ownDeletion = actor === currentUser;

    resetActiveRoomState();
    setStatus("roomStatus", ownDeletion ? t("deletedRoom", { room: deletedRoom }) : t("roomDeletedByOwner", { room: deletedRoom }));
    await loadRooms();
}

async function handleAttachmentSelect(event) {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file || !ensureRoomSelected()) return;

    const caption = document.getElementById("message").value.trim();
    const formData = new FormData();
    formData.append("room_token", currentRoomToken);
    formData.append("text", caption);
    formData.append("file", file);

    setComposerStatus(t("uploadingFile", { file: file.name }));

    try {
        const res = await fetch(`/rooms/${encodeURIComponent(currentRoom)}/attachments`, {
            method: "POST",
            headers: authHeaders({ json: false }),
            body: formData
        });

        const data = await safeJson(res);

        if (!res.ok) {
            setComposerStatus(getApiErrorMessage(data, "uploadFailed"), true);
            return;
        }

        if (shouldAppendHttpResponse()) {
            addMessage(data);
        }

        document.getElementById("message").value = "";
        setComposerStatus(t("fileSent", { file: file.name }));
    } catch (error) {
        setComposerStatus(t("uploadFailed"), true);
    }
}

async function leaveChat() {
    resetActiveRoomState();
    setStatus("roomStatus", t("leftRoom"));
    await loadRooms();
}

function logout() {
    stopRoomsAutoRefresh();

    resetActiveRoomState();
    token = "";
    currentUser = "";
    currentIsAdmin = false;

    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("is_admin");

    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    setStatus("roomStatus", "");
    showLoggedOutState();


}

async function initializeSession() {
    applyTranslations();
    clearChat();

    if (!token || !currentUser) return;

    const ok = await loadMe();
    if (!ok) return;

    showLoggedInState();
    await loadRooms();
    startRoomsAutoRefresh();
}

function handleChatScroll() {
    const chat = document.getElementById("chat");
    if (!chat) return;

    if (
        currentRoom &&
        currentRoomToken &&
        messagesHasMore &&
        !messagesLoading &&
        chat.scrollTop < 80
    ) {
        loadMessages({ older: true });
    }
}

document.addEventListener("visibilitychange", () => {
    if (!document.hidden && token) {
        loadRooms();
    }
});

initializeSession();

document.getElementById("chat").addEventListener("scroll", handleChatScroll);