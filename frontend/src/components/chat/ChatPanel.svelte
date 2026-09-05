<script lang="ts">
    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        roomUsersState
    } from '$lib/state/room-users.svelte';

    import {
        uiState
    } from '$lib/state/ui.svelte';

    import {
        closeChat
    } from '$lib/services/chat-session';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import MessageList
        from './MessageList.svelte';

    import TypingIndicator
        from './TypingIndicator.svelte';

    import MessageContextMenu
        from './MessageContextMenu.svelte';

    import Composer
        from '../composer/Composer.svelte';

    import UsersPopup
        from '../users/UsersPopup.svelte';

    import NotificationButton
        from '../common/NotificationButton.svelte';

    async function toggleUsers() {
        roomUsersState.open =
            !roomUsersState.open;

        if (
            roomUsersState.open &&
            chatState.active
        ) {
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

        event.preventDefault();

        const extension =
            file.type.startsWith(
                'image/'
            )
                ? 'png'
                : 'file';

        const named =
            new File(
                [file],
                file.name ||
                `pasted-${Date.now()}.${extension}`,
                {
                    type: file.type
                }
            );

        composerState
            .setPendingFile(named);
    }
</script>

<svelte:window
    onpaste={handlePaste}
/>

<div class="chat-panel">
    <div class="header">
        <div class="chat-topbar">
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
                        class="secondary small-btn"
                        type="button"
                        onclick={() =>
                            void toggleUsers()}
                    >
                        {t('users')}
                    </button>

                    <button
                        class="secondary small-btn"
                        type="button"
                        onclick={() =>
                            void leave()}
                    >
                        {t('leaveChat')}
                    </button>
                {/if}

                <NotificationButton />

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
                    {uiState.chatFullscreen
                        ? '⮌'
                        : '⛶'}
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