<script lang="ts">
    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        roomUsersState
    } from '$lib/state/room-users.svelte';

    import {
        formatUserCount,
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';

    import Icon
        from '$components/common/Icon.svelte';

    import Avatar
        from '$components/common/Avatar.svelte';
</script>

{#if roomUsersState.open}
    <div class="users-popup">
        <div class="users-card">
            <div class="users-card-header">
                <div>
                    <div class="users-title">
                        {t('onlineUsers')}
                    </div>

                    <div class="users-subtitle">
                        {formatUserCount(
                            roomUsersState
                                .users.length
                        )}
                    </div>
                </div>

                <button
                    class="users-close"
                    type="button"
                    aria-label={t('close')}
                    onclick={() =>
                        roomUsersState.open =
                            false}
                >
                    ×
                </button>
            </div>

            <div class="users-list">
                {#if roomUsersState.loading}
                    <div class="users-loading">
                        {t('loading')}
                    </div>

                {:else if roomUsersState.error}
                    <div class="users-empty">
                        {getApiErrorMessage(
                            roomUsersState.error,
                            'cannotLoadUsers'
                        )}
                    </div>

                {:else if
                    !roomUsersState.users.length}
                    <div class="users-empty">
                        {t('noOnlineUsers')}
                    </div>

                {:else}
                    {#each
                        roomUsersState.users
                        as user
                        (user.username)
                    }
                        <div class="user-item">
                            <Avatar
                                username={user.username}
                                displayName={user.display_name}
                                url={user.avatar_url}
                                size={38}
                                clickToProfile={true}
                            />

                            <div class="user-name">
                                {user.display_name ||
                                    user.username}
                            </div>

                            <div class="user-badges">
                                {#if user.is_admin}
                                    <div
                                        class="user-admin-badge"
                                    >
                                        <Icon name="crown" size={11} />
                                        {t('adminBadge')}
                                    </div>
                                {/if}

                                <div class="user-badge">
                                    {user.username ===
                                    authState.username
                                        ? t('youBadge')
                                        : t('onlineBadge')}
                                </div>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>
    </div>
{/if}