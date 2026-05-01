export const state = {
    token: localStorage.getItem("token") || "",
    currentUser: localStorage.getItem("username") || "",
    currentRoom: "",
    currentRoomToken: "",

    ws: null,

    roomsListCollapsed: false,
    chatFullscreen: false,
    allRooms: [],

    currentLanguage: null,
    suppressNextWsCloseStatus: false,
    roomsRefreshTimer: null,

    currentIsAdmin: localStorage.getItem("is_admin") === "1",

    replyTarget: null,
    contextMessage: null,
    longPressTimer: null,

    typingUsers: new Map(),
    typingStopTimer: null,
    typingRenderTimer: null,

    messagesNextBeforeId: null,
    messagesHasMore: true,
    messagesLoading: false,

    pendingAttachmentFile: null,
    pendingAttachmentUrl: "",

    notificationsEnabled: localStorage.getItem("notifications_enabled") === "1",

    mentionUsers: [],
    mentionDropdownIndex: 0,

    messageCache: new Map(),
};