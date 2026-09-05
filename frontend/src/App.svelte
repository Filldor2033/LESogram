<script lang="ts">
    import { onMount } from 'svelte';

    import LanguageSwitch
        from '$components/common/LanguageSwitch.svelte';

    import AuthPanel
        from '$components/auth/AuthPanel.svelte';

    import RoomsPanel
        from '$components/rooms/RoomsPanel.svelte';

    import ChatPanel
        from '$components/chat/ChatPanel.svelte';

    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        i18n,
        t
    } from '$lib/i18n/i18n.svelte';

    let bootstrapping =
        $state(true);

    onMount(() => {
        let disposed = false;

        async function bootstrap() {
            i18n.syncDocumentLanguage();

            try {
                await authState.initialize();

                if (
                    authState.authenticated &&
                    !disposed
                ) {
                    await roomsState.load();
                }
            } finally {
                if (!disposed) {
                    bootstrapping = false;
                }
            }
        }

        void bootstrap();

        const refreshTimer =
            window.setInterval(
                () => {
                    if (
                        authState.authenticated &&
                        !document.hidden
                    ) {
                        void roomsState.load();
                    }
                },
                10_000
            );

        function visibilityChanged() {
            if (
                !document.hidden &&
                authState.authenticated
            ) {
                void roomsState.load();
            }
        }

        document.addEventListener(
            'visibilitychange',
            visibilityChanged
        );

        return () => {
            disposed = true;

            clearInterval(
                refreshTimer
            );

            document.removeEventListener(
                'visibilitychange',
                visibilityChanged
            );
        };
    });

    async function authenticated() {
        await roomsState.load();
    }
</script>

<svelte:head>
    <title>{t('appTitle')}</title>
</svelte:head>

<div class="container">
    <div class="panel">
        <div class="header">
            <div class="header-row">
                <div class="brand">
                    <div class="brand-mark"></div>

                    <div class="brand-copy">
                        <div class="brand-title">
                            {t('appTitle')}
                        </div>

                        <div class="brand-subtitle">
                            {t('brandSubtitle')}
                        </div>
                    </div>
                </div>

                <LanguageSwitch />
            </div>
        </div>

        {#if bootstrapping}
            <div class="section">
                <div class="status">
                    {t('loadingApp')}
                </div>
            </div>

        {:else if
            !authState.authenticated}
            <AuthPanel
                onAuthenticated={
                    authenticated
                }
            />
        {:else}
            <RoomsPanel />
        {/if}
    </div>

    <ChatPanel />
</div>