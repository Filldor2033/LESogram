<script lang="ts">
    import RoomItem
        from './RoomItem.svelte';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';
</script>

<div id="roomsList">
    {#if roomsState.loading}
        <div class="status">
            {t('loadingRooms')}
        </div>

    {:else if roomsState.items.length === 0}
        <div class="status">
            {t('roomsNone')}
        </div>

    {:else if roomsState.filtered.length === 0}
        <div class="status">
            {t('roomsNotFound')}
        </div>

    {:else}
        {#each
            roomsState.filtered
            as room
            (room.name)
        }
            <RoomItem {room} />
        {/each}
    {/if}
</div>