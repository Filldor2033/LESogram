const en = {
    users: 'Users',
    onlineUsers: 'Online users',
    noOnlineUsers: 'No users online',

    userCount_one: '{count} user',
    userCount_few: '{count} users',
    userCount_many: '{count} users',

    reply: 'Reply',
    close: 'Close',
    edit: 'Edit',
    save: 'Save',
    saved: 'Saved',
    cancel: 'Cancel',
    edited: 'edited',

    cannotEditMessage: 'Cannot edit message',
    onlyAuthorCanEdit:
        'Only the author can edit this message',

    appTitle: 'LESogram',

    brandSubtitle:
        'Fast rooms, live messages, simple sharing',

    authTitle: 'Account',

    usernamePlaceholder: 'Username',
    passwordPlaceholder: 'Password',

    login: 'Login',
    register: 'Register',
    logout: 'Exit',

    adminBadge: 'Admin',
    profileTitle: 'Profile',
    profileTabProfile: 'Profile',
    profileTabSecurity: 'Security',
    profileTabStats: 'Statistics',
    profileTabAdmin: 'Admin',
    profileDisplayName: 'Display name',
    profileBio: 'About me',
    profileBioPlaceholder: 'A couple of words about yourself…',
    profileRegistered: 'Registered',
    profileCurrentPassword: 'Current password',
    profileNewPassword: 'New password',
    profileChangePassword: 'Change password',
    passwordChanged: 'Password changed',
    passwordTooShort: 'Password must be at least 4 characters',
    passwordChangeFailed: 'Could not change the password',
    profileStatTotal: 'messages',
    profileStatRecent: 'In the last 30 days',
    profileStatRooms: 'Rooms active in',
    profileStatFirst: 'First message',
    profileStatText: 'Text messages',
    profileStatImages: 'Images',
    profileStatVideos: 'Videos',
    profileStatVoice: 'Voice messages',
    profileStatFiles: 'Files',
    profileNoStats: 'No statistics yet',
    profileSaveFailed: 'Could not save the profile',
    profileLoadFailed: 'Could not load the profile',
    profileNoBio: 'No bio yet.',
    profileEditSelf: 'Edit my profile',
    avatarUpload: 'Upload avatar',
    avatarRemove: 'Remove',
    avatarHint: 'PNG, JPG, WEBP or GIF, up to 5 MB',
    avatarTooLarge: 'Avatar is too large (max 5 MB)',
    avatarUploadFailed: 'Could not upload the avatar',
    adminUsersTitle: 'Users',
    adminRoomsTitle: 'Rooms',
    adminCreatedBy: 'created by',
    adminGrant: 'Make admin',
    adminRevoke: 'Revoke admin',
    adminActionFailed: 'Action failed',
    youBadge: 'you',

    mentionTitle: "You were mentioned",
    mentionStatus: "@{user} mentioned you",
    onlineBadge: "online",
    createRoomTitle: "Create Room",
    newRoomNamePlaceholder: "New room name",
    roomPasswordPlaceholder: "Room password",
    createRoom: "Create room",
    roomListTitle: "Room List",
    roomListSubtitle: "Browse and join",
    hideList: "Hide list",
    showList: "Show list",
    notificationsEnabled: "Notifications enabled",
    newMessageTitle: "New message in {room}",
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
    returnToChat: "Back to chat: {room}",
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

    videoPlayer: "Video player",

    voiceMessage: "Voice message",
    voiceRecord: "Record voice message",
    voiceCancel: "Cancel recording",
    voiceSendAction: "Send voice message",
    voiceNotSupported: "Voice recording is not supported in this browser",
    voiceInsecure: "Voice recording needs a secure connection — open the site via HTTPS (https://betaversion.lesogram.ru)",
    voiceMicDenied: "Microphone access denied",
    voiceMicBlocked: "Microphone blocked. Check: 1) lock icon in the address bar → Microphone → Allow; 2) global Chrome setting chrome://settings/content/microphone; 3) OS privacy settings (Windows: Settings → Privacy → Microphone; macOS: System Settings → Privacy → Microphone → allow Chrome)",
    voiceMicBlockedApp: "Microphone access denied. Allow it in: Android Settings → Apps → LESogram → Permissions → Microphone",
    voiceNoDevice: "No microphone found on this device",
    voiceMicBusy: "Microphone is unavailable — it may be busy in another app (Discord, Zoom, OBS…). Close it and try again",
    voiceTooShort: "Recording too short",
    sendingVoice: "Sending voice message…",
    voiceSent: "Voice message sent",
    voiceSendFailed: "Failed to send voice message",

    voicePause: "Pause and edit",
    voiceResume: "Continue recording",
    voiceTrimReset: "Reset trim",
    voiceTrimTooShort: "Trimmed fragment is too short (min 0.3s)",
    play: "Play",
    pause: "Pause",
    seek: "Seek",
    volume: "Volume",
    speed: "Playback speed",
    fullscreen: "Fullscreen",
    zoomIn: "Zoom in",
    zoomOut: "Zoom out",
    prev: "Previous",
    next: "Next",
    attachmentLabel: "Attachment",
    fileLabel: "File",
    roomCount_one: "{count} room",
    roomCount_few: "{count} rooms",
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
    uploadCancelled: "Upload cancelled",
    leftRoom: "You left the room",
    systemJoined: "{user} joined",
    systemLeft: "{user} left",
    typingOne: "{user} is typing",
    typingMany: "{users} are typing",
    systemRoomDeleted: "Room was deleted by {user}",
    systemRateLimited: "Too many actions. Please slow down.",
    apiInvalidRoomName: "Room name can contain only letters, numbers, spaces, _ and -",
    apiMissingToken: "Missing token",
    apiInvalidToken: "Invalid token",
    apiUserExists: "User already exists",

    apiUsernameInvalidChars: "Username can only contain Latin and Cyrillic letters, digits, spaces, and _ . -",

    apiUsernameTooShort: "Username must be at least 3 characters",

    apiUsernameTooLong: "Username must be at most 50 characters",

    apiPasswordTooShort: "Password must be at least 4 characters",

    apiPasswordTooLong: "Password must be at most 72 characters",

    authRequirementsHint: "Login: 3–50 characters — letters, digits, _ . - and spaces. Password: 4–72 characters.",
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

    apiTooManyRequests:
        'Too many requests. Retry in {seconds} seconds',

    loading: 'Loading...',
    loadingApp: 'Loading LESogram...',
    loadingRooms: 'Loading rooms...',
    loadingMessages:
        'Loading messages...',
    languageSwitchLabel: 'Language switch',

    cannotLoadUsers:
        'Cannot load users',

    cannotDeleteMessage:
        'Cannot delete message',

    cannotReactMessage:
        'Cannot react to message',

    notificationsDisabled:
        'Notifications disabled',

    notificationsUnsupported:
        'Notifications are not supported by this browser',

    notificationsDenied:
        'Notification permission was denied',

    enableNotifications:
        'Enable notifications',

    disableNotifications:
        'Disable notifications',

    enterFullscreen:
        'Expand chat',

    exitFullscreen:
        'Exit fullscreen',
} as const;

const ru = {
    users: 'Участники',
    onlineUsers: 'Пользователи онлайн',
    noOnlineUsers: 'Нет пользователей онлайн',

    userCount_one: '{count} пользователь',
    userCount_few: '{count} пользователя',
    userCount_many: '{count} пользователей',

    reply: 'Ответить',
    close: 'Закрыть',
    edit: 'Редактировать',
    save: 'Сохранить',
    saved: 'Сохранено',
    cancel: 'Отмена',
    edited: 'изменено',

    cannotEditMessage:
        'Не удалось изменить сообщение',

    onlyAuthorCanEdit:
        'Редактировать сообщение может только автор',

    appTitle: 'LESogram',

    brandSubtitle:
        'Быстрые комнаты, живые сообщения и удобная отправка файлов',

    authTitle: 'Аккаунт',

    usernamePlaceholder: 'Имя пользователя',
    passwordPlaceholder: 'Пароль',

    login: 'Войти',
    register: 'Регистрация',
    logout: 'Выйти',

    adminBadge: 'Админ',
    profileTitle: 'Профиль',
    profileTabProfile: 'Профиль',
    profileTabSecurity: 'Безопасность',
    profileTabStats: 'Статистика',
    profileTabAdmin: 'Админка',
    profileDisplayName: 'Отображаемое имя',
    profileBio: 'О себе',
    profileBioPlaceholder: 'Пара слов о себе…',
    profileRegistered: 'В сети с',
    profileCurrentPassword: 'Текущий пароль',
    profileNewPassword: 'Новый пароль',
    profileChangePassword: 'Сменить пароль',
    passwordChanged: 'Пароль изменён',
    passwordTooShort: 'Пароль должен быть не короче 4 символов',
    passwordChangeFailed: 'Не удалось сменить пароль',
    profileStatTotal: 'сообщений',
    profileStatRecent: 'За последние 30 дней',
    profileStatRooms: 'Активен в комнатах',
    profileStatFirst: 'Первое сообщение',
    profileStatText: 'Текстовые сообщения',
    profileStatImages: 'Изображения',
    profileStatVideos: 'Видео',
    profileStatVoice: 'Голосовые',
    profileStatFiles: 'Файлы',
    profileNoStats: 'Статистики пока нет',
    profileSaveFailed: 'Не удалось сохранить профиль',
    profileLoadFailed: 'Не удалось загрузить профиль',
    profileNoBio: 'Пока ничего не рассказал о себе.',
    profileEditSelf: 'Редактировать профиль',
    avatarUpload: 'Загрузить аватар',
    avatarRemove: 'Удалить',
    avatarHint: 'PNG, JPG, WEBP или GIF, до 5 МБ',
    avatarTooLarge: 'Аватар слишком большой (макс 5 МБ)',
    avatarUploadFailed: 'Не удалось загрузить аватар',
    adminUsersTitle: 'Пользователи',
    adminRoomsTitle: 'Комнаты',
    adminCreatedBy: 'создал:',
    adminGrant: 'Сделать админом',
    adminRevoke: 'Разжаловать',
    adminActionFailed: 'Не удалось выполнить',
    youBadge: 'вы',

    mentionTitle: "Вас упомянули",
    mentionStatus: "@{user} упомянул(а) вас",
    onlineBadge: "онлайн",
    createRoomTitle: "Создать комнату",
    newRoomNamePlaceholder: "Название новой комнаты",
    roomPasswordPlaceholder: "Пароль комнаты",
    createRoom: "Создать комнату",
    roomListTitle: "Список комнат",
    roomListSubtitle: "Выберите и подключитесь",
    hideList: "Скрыть",
    showList: "Показать",
    notificationsEnabled: "Уведомления включены",
    newMessageTitle: "Новое сообщение в {room}",
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
    returnToChat: "Вернуться в чат: {room}",
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

    videoPlayer: "Видеоплеер",

    voiceMessage: "Голосовое сообщение",
    voiceRecord: "Записать голосовое сообщение",
    voiceCancel: "Отменить запись",
    voiceSendAction: "Отправить голосовое",
    voiceNotSupported: "Запись голоса не поддерживается в этом браузере",
    voiceInsecure: "Для записи голоса нужно защищённое соединение — откройте сайт по HTTPS (https://betaversion.lesogram.ru)",
    voiceMicDenied: "Нет доступа к микрофону",
    voiceMicBlocked: "Микрофон заблокирован. Проверьте: 1) замок в адресной строке → Микрофон → Разрешить; 2) глобальная настройка Chrome chrome://settings/content/microphone; 3) доступ ОС (Windows: Параметры → Конфиденциальность → Микрофон; macOS: Системные настройки → Конфиденциальность → Микрофон → разрешить Chrome)",
    voiceMicBlockedApp: "Нет доступа к микрофону. Разрешите его в: Настройки Android → Приложения → LESogram → Разрешения → Микрофон",
    voiceNoDevice: "На устройстве не найден микрофон",
    voiceMicBusy: "Микрофон недоступен — возможно, он занят другим приложением (Discord, Zoom, OBS…). Закройте его и попробуйте снова",
    voiceTooShort: "Слишком короткая запись",
    sendingVoice: "Отправка голосового…",
    voiceSent: "Голосовое отправлено",
    voiceSendFailed: "Не удалось отправить голосовое",

    voicePause: "Пауза и редактирование",
    voiceResume: "Продолжить запись",
    voiceTrimReset: "Сбросить обрезку",
    voiceTrimTooShort: "Обрезанный фрагмент слишком короткий (мин. 0.3с)",
    play: "Воспроизвести",
    pause: "Пауза",
    seek: "Перемотка",
    volume: "Громкость",
    speed: "Скорость воспроизведения",
    fullscreen: "Полный экран",
    zoomIn: "Приблизить",
    zoomOut: "Отдалить",
    prev: "Предыдущее",
    next: "Следующее",
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
    uploadCancelled: "Загрузка отменена",
    leftRoom: "Вы вышли из комнаты",
    systemJoined: "{user} вошёл(а)",
    systemLeft: "{user} вышел(а)",
    typingOne: "{user} печатает",
    typingMany: "{users} печатают",
    systemRoomDeleted: "Комната удалена пользователем {user}",
    systemRateLimited: "Слишком много действий. Немного подождите.",
    apiInvalidRoomName: "Название комнаты может содержать только буквы, цифры, пробелы, _ и -",
    apiMissingToken: "Токен отсутствует",
    apiInvalidToken: "Недействительный токен",
    apiUserExists: "Пользователь уже существует",

    apiUsernameInvalidChars: "Имя пользователя может содержать только латиницу и кириллицу, цифры, пробелы и _ . -",

    apiUsernameTooShort: "Имя пользователя — минимум 3 символа",

    apiUsernameTooLong: "Имя пользователя — максимум 50 символов",

    apiPasswordTooShort: "Пароль — минимум 4 символа",

    apiPasswordTooLong: "Пароль — максимум 72 символа",

    authRequirementsHint: "Логин: 3–50 символов — буквы, цифры, _ . - и пробелы. Пароль: 4–72 символа.",
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
    apiTooManyRequests: "Слишком много запросов. Повторите через {seconds} сек.",

    loading: 'Загрузка...',
    loadingApp: 'Загрузка LESogram...',
    loadingRooms: 'Загрузка комнат...',
    loadingMessages:
        'Загрузка сообщений...',
    languageSwitchLabel: 'Переключение языка',
    cannotLoadUsers:
    'Не удалось загрузить пользователей',

    cannotDeleteMessage:
        'Не удалось удалить сообщение',

    cannotReactMessage:
        'Не удалось изменить реакцию',

    notificationsDisabled:
        'Уведомления выключены',

    notificationsUnsupported:
        'Браузер не поддерживает уведомления',

    notificationsDenied:
        'Доступ к уведомлениям запрещён',

    enableNotifications:
        'Включить уведомления',

    disableNotifications:
        'Выключить уведомления',

    enterFullscreen:
        'Развернуть чат',

    exitFullscreen:
        'Выйти из полноэкранного режима',
} satisfies Record<TranslationKey, string>;

export type TranslationKey =
    keyof typeof en;

export type TranslationVars =
    Record<string, string | number>;

export const translations = {
    en,
    ru
} satisfies Record<
    'en' | 'ru',
    Record<TranslationKey, string>
>;

export type Language =
    keyof typeof translations;