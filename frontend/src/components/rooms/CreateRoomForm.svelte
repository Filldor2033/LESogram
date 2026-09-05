<script lang="ts">
    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';

    let name = $state('');
    let password = $state('');

    let creating = $state(false);

    let error = $state<unknown>(null);

    let createdRoom =
        $state<string | null>(null);

    async function submit() {
        const roomName = name.trim();

        error = null;
        createdRoom = null;

        if (
            !roomName ||
            !password
        ) {
            error = new Error(
                'ROOM_DATA_MISSING'
            );

            return;
        }

        if (creating) {
            return;
        }

        creating = true;

        try {
            await roomsState.create(
                roomName,
                password
            );

            createdRoom = roomName;

            name = '';
            password = '';
        } catch (cause) {
            error = cause;
        } finally {
            creating = false;
        }
    }
</script>

<div class="section-block">
    <div class="section-title">
        {t('createRoomTitle')}
    </div>

    <form
        onsubmit={(event) => {
            event.preventDefault();
            submit();
        }}
    >
        <input
            bind:value={name}
            placeholder={
                t('newRoomNamePlaceholder')
            }
            autocomplete="off"
        />

        <input
            bind:value={password}
            type="password"
            placeholder={
                t('roomPasswordPlaceholder')
            }
            autocomplete="new-password"
        />

        <button
            type="submit"
            disabled={
                creating ||
                !name.trim() ||
                !password
            }
        >
            {t('createRoom')}
        </button>
    </form>

    <div
        class:error={Boolean(error)}
        class="status"
    >
        {#if error}
            {error instanceof Error &&
            error.message ===
                'ROOM_DATA_MISSING'
                ? t('fillRoomData')
                : getApiErrorMessage(
                    error,
                    'cannotCreateRoom'
                )}

        {:else if createdRoom}
            {t(
                'roomCreated',
                {
                    room: createdRoom
                }
            )}
        {/if}
    </div>
</div>