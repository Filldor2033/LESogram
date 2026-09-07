import type { Snippet } from 'svelte';

export type IconName =
    | 'reply'
    | 'edit'
    | 'trash'
    | 'bell'
    | 'bell-off'
    | 'paperclip'
    | 'download'
    | 'file'
    | 'file-text'
    | 'archive'
    | 'image'
    | 'video'
    | 'audio'
    | 'check'
    | 'close'
    | 'mention'
    | 'send'
    | 'users'
    | 'plus'
    | 'search'
    | 'refresh'
    | 'logout'
    | 'chevron-down'
    | 'chevron-left'
    | 'chevron-right'
    | 'copy'
    | 'expand'
    | 'collapse'
    | 'play'
    | 'pause'
    | 'volume'
    | 'volume-off'
    | 'zoom-in'
    | 'zoom-out'
    | 'skip-back'
    | 'skip-forward'
    | 'crown'
    | 'mic'
    | 'stop';

interface IconProps {
    name: IconName;
    size?: number;
    width?: number;
    height?: number;
    class?: string;
    children?: Snippet;
}

const PATHS: Record<IconName, string> = {
    'reply':
        'M9 17l-5-5 5-5M4 12h9a7 7 0 0 1 7 7v1',
    'edit':
        'M12 20h8M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z',
    'trash':
        'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
    'bell':
        'M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8M13.7 21a2 2 0 0 1-3.4 0',
    'bell-off':
        'M8.7 4.1A6 6 0 0 1 18 8c0 7 3 8 3 8M6.3 6.3C6.1 6.8 6 7.4 6 8c0 7-3 8-3 8h13M13.7 21a2 2 0 0 1-3.4 0M3 3l18 18',
    'paperclip':
        'M21.4 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.2-9.19a4 4 0 0 1 5.65 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48',
    'download':
        'M12 3v12M7 10l5 5 5-5M4 21h16',
    'file':
        'M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-7-6zM14 3v6h6M9 14h6M9 17h4',
    'file-text':
        'M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-7-6zM14 3v6h6M9 12h6M9 16h6',
    'archive':
        'M4 8h16v12H4zM2 4h20v4H2zM10 12h4M12 3v5',
    'image':
        'M4 16l4.6-4.6a2 2 0 0 1 2.8 0L16 16M14 14l1.3-1.3a2 2 0 0 1 2.8 0L22 16M3 5h18v14H3zM3 5v14h18V5z',
    'video':
        'M15 10l6-3v10l-6-3M3 6a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6z',
    'audio':
        'M9 18V6l10-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM19 16a3 3 0 1 1-6 0 3 3 0 0 1 6 0z',
    'check':
        'M20 6L9 17l-5-5',
    'close':
        'M18 6L6 18M6 6l12 12',
    'mention':
        'M12 16v-5a2 2 0 1 0-4 0v1M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0zm0 0v1.5a2.5 2.5 0 0 0 5 0V12a9 9 0 1 0-5.5 8.3',
    'send':
        'M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z',
    'users':
        'M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM21 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
    'plus':
        'M12 5v14M5 12h14',
    'search':
        'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.35-4.35',
    'refresh':
        'M21 12a9 9 0 1 1-2.64-6.36M21 3v6h-6',
    'logout':
        'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9',
    'chevron-down':
        'M6 9l6 6 6-6',
    'chevron-left':
        'M15 18l-6-6 6-6',
    'chevron-right':
        'M9 6l6 6-6 6',
    'copy':
        'M9 9h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V11a2 2 0 0 1 2-2zM5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1',
    'expand':
        'M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3',
    'collapse':
        'M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7',
    'play':
        'M6 4l14 8-14 8V4z',
    'pause':
        'M7 4v16M17 4v16',
    'volume':
        'M11 5L6 9H3v6h3l5 4V5zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13',
    'volume-off':
        'M11 5L6 9H3v6h3l5 4V5zM22 9l-6 6M16 9l6 6',
    'zoom-in':
        'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.35-4.35M11 8v6M8 11h6',
    'zoom-out':
        'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.35-4.35M8 11h6',
    'skip-back':
        'M19 20L9 12l10-8v16zM5 19V5',
    'skip-forward':
        'M5 4l10 8-10 8V4zM19 5v14',
    'crown':
        'M3 8l4 4 5-6 5 6 4-4v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zM5 21h14',
    'mic':
        'M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3zM19 10v1a7 7 0 0 1-14 0v-1M12 18v4M8 22h8',
    'stop':
        'M6 6h12v12H6z'
};

export function iconPath(name: IconName): string {
    return PATHS[name] ?? '';
}

export function fileIconName(mimeOrName = ''): IconName {
    const value = mimeOrName.toLowerCase();

    if (value.includes('pdf') || value.endsWith('.pdf')) {
        return 'file-text';
    }

    if (
        value.includes('zip') ||
        value.includes('rar') ||
        value.includes('7z') ||
        value.endsWith('.zip') ||
        value.endsWith('.rar') ||
        value.endsWith('.7z')
    ) {
        return 'archive';
    }

    if (value.includes('image') || /\.(png|jpe?g|gif|webp)$/.test(value)) {
        return 'image';
    }

    if (value.includes('video') || /\.(mp4|webm|mov)$/.test(value)) {
        return 'video';
    }

    if (value.includes('audio') || /\.(mp3|wav|ogg|m4a)$/.test(value)) {
        return 'audio';
    }

    if (value.includes('text') || value.includes('word') || value.endsWith('.txt')) {
        return 'file-text';
    }

    return 'file';
}
