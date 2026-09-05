<script lang="ts">
    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';

    let {
        onAuthenticated
    }: {
        onAuthenticated?: () =>
            void | Promise<void>;
    } = $props();

    let username = $state('');
    let password = $state('');

    let loading = $state(false);
    let error = $state<unknown>(null);

    async function authenticate(
        mode: 'login' | 'register'
    ) {
        if (
            !username.trim() ||
            !password
        ) {
            error = new Error('AUTH_FILL');
            return;
        }

        loading = true;
        error = null;

        try {
            const credentials = {
                username: username.trim(),
                password
            };

            if (mode === 'login') {
                await authState.login(
                    credentials
                );
            } else {
                await authState.register(
                    credentials
                );
            }

            password = '';

            await onAuthenticated?.();
        } catch (cause) {
            error = cause;
        } finally {
            loading = false;
        }
    }
</script>

<div
    class="section"
    id="authSection"
>
    <div class="section-block">
        <div class="section-title">
            {t('authTitle')}
        </div>

        <input
            bind:value={username}
            placeholder={t('usernamePlaceholder')}
            autocomplete="username"
        />

        <input
            bind:value={password}
            type="password"
            placeholder={t('passwordPlaceholder')}
            autocomplete="current-password"
        />

        <button
            type="button"
            disabled={loading}
            onclick={() =>
                authenticate('login')}
        >
            {t('login')}
        </button>

        <div style="height:8px"></div>

        <button
            class="secondary"
            type="button"
            disabled={loading}
            onclick={() =>
                authenticate('register')}
        >
            {t('register')}
        </button>

        <div
            class:error={Boolean(error)}
            class="status"
        >
            {#if error}
                {error instanceof Error &&
                error.message === 'AUTH_FILL'
                    ? t('authFill')
                    : getApiErrorMessage(
                        error,
                        'authFailed'
                    )}
            {/if}
        </div>
    </div>
</div>