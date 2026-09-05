<script lang="ts">
    import CreateRoomForm
        from './CreateRoomForm.svelte';

    import RoomFilters
        from './RoomFilters.svelte';

    import RoomList
        from './RoomList.svelte';

    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        uiState
    } from '$lib/state/ui.svelte';

    import {
        formatRoomCount,
        t
    } from '$lib/i18n/i18n.svelte';

    import Icon
        from '$components/common/Icon.svelte';

    function logout() {
        roomsState.clear();
        authState.logout();
    }
</script>

<div
    class="section"
    id="roomsSection"
>
    {#if chatState.active}
        <button
            class="return-to-chat"
            type="button"
            onclick={() =>
                uiState
                    .showMobileChat()}
        >
            <Icon
                name="chevron-right"
                size={16}
            />

            <span>
                {t(
                    'returnToChat',
                    {
                        room:
                            roomsState
                                .currentRoom
                    }
                )}
            </span>
        </button>
    {/if}

    <div class="topbar">
        <div class="whoami-row">
            <b>
                {authState.username}
            </b>

            {#if authState.isAdmin}
                <span class="admin-badge">
                    {t('adminBadge')}
                </span>
            {/if}
        </div>

        <button
            class="secondary small-btn"
            type="button"
            onclick={logout}
        >
            {t('logout')}
        </button>
    </div>

    <hr
        style="
            border-color:#1f2937;
            opacity:.4;
            margin:16px 0
        "
    />

    <CreateRoomForm />

    <hr
        style="
            border-color:#1f2937;
            opacity:.4;
            margin:16px 0
        "
    />

    <div class="section-block">
        <div class="section-title-row">
            <div
                class="section-title"
                style="margin-bottom:0"
            >
                {t('roomListTitle')}
            </div>

            <div class="section-pill">
                {formatRoomCount(
                    roomsState.items.length
                )}
            </div>
        </div>

        <div class="rooms-list-header">
            <div class="rooms-list-title">
                {t('roomListSubtitle')}
            </div>

            <button
                class="secondary small-btn"
                type="button"
                onclick={() => {
                    roomsState.collapsed =
                        !roomsState.collapsed;
                }}
            >
                {roomsState.collapsed
                    ? t('showList')
                    : t('hideList')}
            </button>
        </div>

        {#if !roomsState.collapsed}
            <div id="roomsListSection">
                <RoomFilters />
                <RoomList />
            </div>
        {/if}
    </div>
</div>
