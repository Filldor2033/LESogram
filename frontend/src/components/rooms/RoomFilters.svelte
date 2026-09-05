<script lang="ts">
    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    async function refresh() {
        await roomsState.load();
    }
</script>

<div class="filters">
    <input
        bind:value={roomsState.roomSearch}
        placeholder={
            t('roomSearchPlaceholder')
        }
    />

    <input
        bind:value={roomsState.creatorSearch}
        placeholder={
            t('creatorSearchPlaceholder')
        }
    />

    <div class="filters-row">
        <select
            bind:value={
                roomsState.onlineFilter
            }
        >
            <option value="all">
                {t('allRooms')}
            </option>

            <option value="online">
                {t('onlineOnly')}
            </option>

            <option value="empty">
                {t('emptyOnly')}
            </option>
        </select>

        <select
            bind:value={roomsState.sort}
        >
            <option value="name_asc">
                {t('sortNameAsc')}
            </option>

            <option value="name_desc">
                {t('sortNameDesc')}
            </option>

            <option value="online_desc">
                {t('sortOnlineDesc')}
            </option>

            <option value="online_asc">
                {t('sortOnlineAsc')}
            </option>

            <option value="creator_asc">
                {t('sortCreatorAsc')}
            </option>
        </select>
    </div>

    <div class="filters-row">
        <button
            class="secondary"
            type="button"
            onclick={refresh}
        >
            {t('refreshRooms')}
        </button>

        <button
            class="secondary"
            type="button"
            onclick={() =>
                roomsState.resetFilters()}
        >
            {t('resetFilters')}
        </button>
    </div>
</div>