import {
    i18n
} from '$lib/i18n/i18n.svelte';

export function formatTime(
    iso?: string | null
): string {
    if (!iso) {
        return '';
    }

    const date =
        new Date(iso);

    return date.toLocaleTimeString(
        i18n.language === 'ru'
            ? 'ru-RU'
            : 'en-US',
        {
            hour: '2-digit',
            minute: '2-digit'
        }
    );
}