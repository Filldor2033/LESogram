<script lang="ts">
    import {
        notificationsState
    } from '$lib/state/notifications.svelte';

    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    async function toggle() {
        const result =
            await notificationsState
                .toggle();

        switch (result) {
            case 'enabled':
                composerState.setStatus(
                    'notificationsEnabled'
                );
                break;

            case 'disabled':
                composerState.setStatus(
                    'notificationsDisabled'
                );
                break;

            case 'unsupported':
                composerState.setStatus(
                    'notificationsUnsupported',
                    {},
                    true
                );
                break;

            case 'denied':
                composerState.setStatus(
                    'notificationsDenied',
                    {},
                    true
                );
                break;
        }
    }
</script>

<button
    class:secondary={
        !notificationsState.enabled
    }
    class="small-btn toggle-btn"
    type="button"
    title={
        notificationsState.enabled
            ? t('disableNotifications')
            : t('enableNotifications')
    }
    aria-label={
        notificationsState.enabled
            ? t('disableNotifications')
            : t('enableNotifications')
    }
    onclick={() => void toggle()}
>
    {notificationsState.enabled
        ? '🔔'
        : '🔕'}
</button>