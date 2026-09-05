import {
    i18n
} from '$lib/i18n/i18n.svelte';

const UNITS = [
    'B',
    'KB',
    'MB',
    'GB',
    'TB'
] as const;

export function formatBytes(
    bytes?: number | null
): string {
    if (
        bytes == null ||
        !Number.isFinite(bytes) ||
        bytes <= 0
    ) {
        return '';
    }

    const index = Math.min(
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        ),
        UNITS.length - 1
    );

    const value =
        bytes / Math.pow(1024, index);

    return `${new Intl.NumberFormat(
        i18n.language === 'ru'
            ? 'ru-RU'
            : 'en-US',
        {
            maximumFractionDigits:
                index === 0 ? 0 : 1
        }
    ).format(value)} ${UNITS[index]}`;
}

export function getFileIcon(
    type = ''
): string {
    if (type.includes('pdf')) {
        return '📄';
    }

    if (
        type.includes('zip') ||
        type.includes('rar') ||
        type.includes('7z')
    ) {
        return '🗜️';
    }

    if (type.includes('text')) {
        return '📝';
    }

    return '📎';
}