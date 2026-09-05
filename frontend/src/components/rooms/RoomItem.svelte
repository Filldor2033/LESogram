<script lang="ts">
    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';

    import type {
        Room
    } from '$lib/types/room';

    import {
        openChat
    } from '$lib/services/chat-session';

    let {
        room
    }: {
        room: Room;
    } = $props();

    let password = $state('');

    let joining = $state(false);
    let deleting = $state(false);

    let error = $state<unknown>(null);

    let canDelete = $derived(
        room.created_by ===
            authState.username ||
        authState.isAdmin
    );

    async function join() {
        error = null;

        if (
            !authState.isAdmin &&
            !password
        ) {
            error =
                new Error(
                    'ROOM_PASSWORD_REQUIRED'
                );

            return;
        }

        joining = true;

        try {
            const roomToken = await roomsState.join(
                room,
                password
            );

            await openChat(
                room.name,
                roomToken
            );

            roomsState.collapsed = true;

            await roomsState.load();

            password = '';
        } catch (cause) {
            error = cause;
        } finally {
            joining = false;
        }
    }

    async function remove() {
        const confirmed =
            confirm(
                t(
                    'confirmDeleteRoom',
                    {
                        room: room.name
                    }
                )
            );

        if (!confirmed) {
            return;
        }

        deleting = true;
        error = null;

        try {
            await roomsState.delete(
                room
            );
        } catch (cause) {
            error = cause;
        } finally {
            deleting = false;
        }
    }
</script>

<div class="room-item">
    <div class="room-title">
        {room.name}
    </div>

    <div class="room-meta">
        <div>
            {t('creatorLabel')}:
            {room.created_by}
        </div>

        <div>
            {t('onlineLabel')}:
            {room.online}
        </div>
    </div>

    {#if !authState.isAdmin}
        <input
            bind:value={password}
            type="password"
            placeholder={
                t('roomPasswordPlaceholder')
            }
            autocomplete="off"
            onkeydown={(event) => {
                if (event.key === 'Enter') {
                    void join();
                }
            }}
        />
    {/if}

    <div class="room-actions">
        <button
            type="button"
            disabled={joining}
            onclick={join}
        >
            {t('join')}
        </button>

        {#if canDelete}
            <button
                class="danger"
                type="button"
                disabled={deleting}
                onclick={remove}
            >
                {t('delete')}
            </button>
        {/if}
    </div>

    {#if error}
        <div class="status error">
            {error instanceof Error &&
            error.message ===
                'ROOM_PASSWORD_REQUIRED'
                ? t('enterRoomPassword')
                : getApiErrorMessage(
                    error,
                    'cannotJoinRoom'
                )}
        </div>
    {/if}
</div>