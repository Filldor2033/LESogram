<script lang="ts">
    import { fly } from 'svelte/transition';

    import Avatar from '$components/common/Avatar.svelte';

    import { authState } from '$lib/state/auth.svelte';
    import { profileState } from '$lib/state/profile.svelte';

    import { t } from '$lib/i18n/i18n.svelte';
</script>

<button
    class="profile-btn"
    type="button"
    title={t('profileTitle')}
    aria-label={t('profileTitle')}
    in:fly={{ y: 6, duration: 160 }}
    onclick={() => (profileState.open = true)}
>
    <Avatar
        username={authState.username}
        displayName={profileState.displayName}
        url={profileState.avatarUrl}
        size={24}
    />

    <span class="profile-btn-name">
        {profileState.displayName || authState.username}
    </span>
</button>
