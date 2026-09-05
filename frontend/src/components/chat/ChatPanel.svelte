<script lang="ts">
    import {
        onMount
    } from 'svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        roomUsersState
    } from '$lib/state/room-users.svelte';

    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        uiState
    } from '$lib/state/ui.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        closeChat
    } from '$lib/services/chat-session';

    import Icon
        from '$components/common/Icon.svelte';

    import NotificationButton
        from '$components/common/NotificationButton.svelte';

    import UsersPopup
        from '$components/users/UsersPopup.svelte';

    import MessageList
        from './MessageList.svelte';

    import MessageContextMenu
        from './MessageContextMenu.svelte';

    import TypingIndicator
        from './TypingIndicator.svelte';

    import Composer
        from '$components/composer/Composer.svelte';

    async function toggleUsers() {
        if (
            roomUsersState.open &&
            chatState.active
        ) {
            roomUsersState.close();
            return;
        }

        if (
            !roomUsersState.open &&
            chatState.active
        ) {
            roomUsersState.open = true;

            await roomUsersState.refresh(
                chatState.room,
                chatState.roomToken
            );
        }
    }

    async function leave() {
        closeChat();

        composerState.reset();
        roomUsersState.clear();

        roomsState.leave();
        roomsState.collapsed = false;

        await roomsState.load();
    }

    function handlePaste(
        event: ClipboardEvent
    ) {
        if (!chatState.active) {
            return;
        }

        const items =
            Array.from(
                event.clipboardData
                    ?.items ?? []
            );

        const fileItem =
            items.find(
                item =>
                    item.kind === 'file'
            );

        if (!fileItem) {
            return;
        }

        const file =
            fileItem.getAsFile();

        if (!file) {
            return;
        }

        const named =
            file.name ||
            `clipboard-${Date.now()}`;

        const typed =
            file.type ||
            'application/octet-stream';

        const renamed =
            new File(
                [file],
                named,
                { type: typed }
            );

        composerState
            .setPendingFile(renamed);
    }
</script>

<svelte:window
    onpaste={handlePaste}
/>

<div class="chat-panel">
    <div class="header">
        <div class="chat-topbar">
            <button
                class="secondary small-btn mobile-back"
                type="button"
                title={t('showList')}
                aria-label={t('showList')}
                onclick={() =>
                    uiState
                        .showMobileRooms()}
            >
                <Icon
                    name="chevron-left"
                    size={17}
                />
            </button>

            <div class="chat-room-label">
                <div class="chat-room-dot"></div>

                <div class="chat-room-copy">
                    <span>
                        {roomsState.currentRoom
                            ? t(
                                'roomHeader',
                                {
                                    room:
                                        roomsState
                                            .currentRoom
                                }
                            )
                            : t(
                                'chatNotSelected'
                            )}
                    </span>

                    <small>
                        {roomsState.currentRoom
                            ? t('realtimeActive')
                            : t('chooseRoom')}
                    </small>
                </div>
            </div>

            <div class="chat-actions">
                {#if chatState.active}
                    <button
                        class="secondary small-btn users-btn"
                        type="button"
                        title={t('users')}
                        aria-label={t('users')}
                        onclick={() =>
                            void toggleUsers()}
                    >
                        <Icon
                            name="users"
                            size={16}
                        />

                        <span class="btn-label">
                            {t('users')}
                        </span>
                    </button>

                    <button
                        class="secondary small-btn leave-btn"
                        type="button"
                        title={t('leaveChat')}
                        aria-label={t('leaveChat')}
                        onclick={() =>
                            void leave()}
                    >
                        <Icon
                            name="logout"
                            size={16}
                        />

                        <span class="btn-label">
                            {t('leaveChat')}
                        </span>
                    </button>
                {/if}

                <NotificationButton />

                <button
                    class="secondary small-btn sidebar-toggle"
                    type="button"
                    title={
                        uiState.fsSidebarHidden
                            ? t('showList')
                            : t('hideList')
                    }
                    aria-label={
                        uiState.fsSidebarHidden
                            ? t('showList')
                            : t('hideList')
                    }
                    onclick={() =>
                        uiState
                            .toggleFsSidebar()}
                >
                    <Icon
                        name="chevron-left"
                        size={17}
                        class={
                            uiState
                                .fsSidebarHidden
                                ? 'flip'
                                : ''
                        }
                    />
                </button>

                <button
                    class="secondary small-btn"
                    type="button"
                    title={
                        uiState.chatFullscreen
                            ? t('exitFullscreen')
                            : t('enterFullscreen')
                    }
                    aria-label={
                        uiState.chatFullscreen
                            ? t('exitFullscreen')
                            : t('enterFullscreen')
                    }
                    onclick={() =>
                        uiState
                            .toggleChatFullscreen()}
                >
                    <Icon
                        name={
                            uiState.chatFullscreen
                                ? 'collapse'
                                : 'expand'
                        }
                        size={17}
                    />
                </button>
            </div>
        </div>
    </div>

    <UsersPopup />

    <MessageList />

    <TypingIndicator />

    <Composer />

    <MessageContextMenu />
</div>
