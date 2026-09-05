<script lang="ts">
    import {
        i18n,
        t
    } from '$lib/i18n/i18n.svelte';

    $effect(() => {
        i18n.syncDocumentLanguage();
    });
</script>

<div
    class="lang-switch"
    aria-label={t('languageSwitchLabel')}
>
    <button
        class="lang-btn"
        class:active={i18n.language === 'en'}
        type="button"
        aria-pressed={i18n.language === 'en'}
        onclick={() => i18n.setLanguage('en')}
    >
        EN
    </button>

    <button
        class="lang-btn"
        class:active={i18n.language === 'ru'}
        type="button"
        aria-pressed={i18n.language === 'ru'}
        onclick={() => i18n.setLanguage('ru')}
    >
        RU
    </button>
</div>