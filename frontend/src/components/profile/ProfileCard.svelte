<script lang="ts">
    import { fade, scale } from 'svelte/transition';

    import Avatar from '$components/common/Avatar.svelte';
    import Icon from '$components/common/Icon.svelte';

    import { authState } from '$lib/state/auth.svelte';
    import { profileState } from '$lib/state/profile.svelte';

    import { getPublicProfile } from '$lib/api/profile';

    import { t } from '$lib/i18n/i18n.svelte';

    import type { PublicProfile } from '$lib/types/auth';

    let profile = $state<PublicProfile | null>(null);
    let loading = $state(false);
    let error = $state(false);

    // fetch whenever a username is opened
    $effect(() => {
        const username = profileState.viewing;

        if (!username) {
            profile = null;
            return;
        }

        profile = null;
        error = false;
        loading = true;

        getPublicProfile(authState.token, username)
            .then((data) => {
                profile = data;
            })
            .catch(() => {
                error = true;
            })
            .finally(() => {
                loading = false;
            });
    });

    // click on own avatar/name opens the cabinet instead
    const isSelf = $derived(
        profileState.viewing === authState.username
    );
</script>

{#if profileState.viewing}
    <div
        class="modal-overlay"
        transition:fade={{ duration: 140 }}
        onclick={() => (profileState.viewing = null)}
        role="presentation"
    >
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
        <!-- svelte-ignore a11y_interactive_supports_focus -->
        <div
            class="modal profile-modal profile-card"
            transition:scale={{ duration: 160, start: 0.96 }}
            onclick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label={t('profileTitle')}
        >
            {#if loading}
                <div class="profile-empty">
                    {t('loading')}
                </div>
            {:else if error}
                <div class="profile-empty">
                    {t('profileLoadFailed')}
                </div>
            {:else if profile}
                <div class="profile-head">
                    <Avatar
                        username={profile.username}
                        displayName={profile.display_name}
                        url={profile.avatar_url}
                        size={64}
                    />

                    <div class="profile-head-info">
                        <div class="profile-head-name">
                            {profile.display_name ||
                                profile.username}
                        </div>

                        <div class="profile-head-sub">
                            @{profile.username}
                            {#if profile.is_admin}
                                <span class="admin-chip">
                                    {t('adminBadge')}
                                </span>
                            {/if}
                        </div>
                    </div>

                    <button
                        class="profile-close"
                        type="button"
                        aria-label={t('close')}
                        onclick={() =>
                            (profileState.viewing = null)}
                    >
                        ×
                    </button>
                </div>

                {#if profile.bio}
                    <div class="profile-card-bio">
                        {profile.bio}
                    </div>
                {:else}
                    <div class="profile-card-bio empty">
                        {t('profileNoBio')}
                    </div>
                {/if}

                {#if isSelf}
                    <button
                        class="profile-card-edit"
                        type="button"
                        onclick={() => {
                            profileState.viewing = null;
                            profileState.open = true;
                        }}
                    >
                        {t('profileEditSelf')}
                    </button>
                {/if}
            {/if}
        </div>
    </div>
{/if}
