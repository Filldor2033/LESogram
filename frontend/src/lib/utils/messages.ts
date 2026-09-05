import {
    t
} from '$lib/i18n/i18n.svelte';

import type {
    Message
} from '$lib/types/message';

export interface MessageTextPart {
    text: string;
    mention: boolean;
}

export function getSystemMessageText(
    message: Message
): string {
    const actor =
        message.system_actor ||
        message.username ||
        '';

    switch (
        message.system_event
    ) {
        case 'joined':
            return t(
                'systemJoined',
                {
                    user: actor
                }
            );

        case 'left':
            return t(
                'systemLeft',
                {
                    user: actor
                }
            );

        case 'room_deleted':
            return t(
                'systemRoomDeleted',
                {
                    user: actor
                }
            );

        case 'rate_limited':
            return t(
                'systemRateLimited'
            );

        default:
            return message.text ?? '';
    }
}

export function getReplyPreview(
    message?: Message
): string {
    if (!message) {
        return '';
    }

    const text =
        message.text?.trim();

    if (text) {
        return text;
    }

    if (message.file_name) {
        return message.file_name;
    }

    return t('attachmentLabel');
}

export function splitMessageText(
    text: string
): MessageTextPart[] {
    const regex =
        /(@[A-Za-z0-9_а-яА-ЯёЁ-]+)/g;

    return text
        .split(regex)
        .filter(Boolean)
        .map(part => ({
            text: part,
            mention:
                /^@[A-Za-z0-9_а-яА-ЯёЁ-]+$/
                    .test(part)
        }));
}