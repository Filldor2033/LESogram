import {
    t
} from '$lib/i18n/i18n.svelte';

import type {
    TranslationKey
} from './translations';

import {
    ApiError
} from '$lib/api/http';

const API_DETAIL_MAP: Record<
    string,
    TranslationKey
> = {
    'Missing token':
        'apiMissingToken',

    'Invalid token':
        'apiInvalidToken',

    'User already exists':
        'apiUserExists',

    'Invalid credentials':
        'apiInvalidCredentials',

    'Room already exists':
        'apiRoomExists',

    'Room not found':
        'apiRoomNotFound',

    'Wrong room password':
        'apiWrongRoomPassword',

    'No access to this room':
        'apiNoRoomAccess',

    'Only the creator can delete this room':
        'apiDeleteDenied',

    'Attachment is missing a file name':
        'apiAttachmentMissingName',

    'Attachment not found':
        'apiAttachmentNotFound',

    'File type is not allowed':
        'apiFileTypeNotAllowed',

    'GIF uploads are disabled':
        'apiGifDisabled',

    'Attachment is empty':
        'apiAttachmentEmpty',

    'Message cannot be empty':
        'apiMessageEmpty',

    'Room name can contain only letters, numbers, spaces, _ and -':
        'apiInvalidRoomName',

    'Only the author can edit this message':
        'onlyAuthorCanEdit'
};

function extractDetail(
    data: unknown
): unknown {
    if (
        typeof data !== 'object' ||
        data === null
    ) {
        return data;
    }

    if ('detail' in data) {
        return data.detail;
    }

    return data;
}

export function translateApiDetail(
    detail: unknown
): string {
    if (
        typeof detail !== 'string' ||
        !detail
    ) {
        return '';
    }

    const direct =
        API_DETAIL_MAP[detail];

    if (direct) {
        return t(direct);
    }

    let match = detail.match(
        /^Attachment is too large\. Max size is (\d+) MB$/
    );

    if (match) {
        return t(
            'apiAttachmentTooLarge',
            {
                size: match[1]
            }
        );
    }

    match = detail.match(
        /^Message must be at most (\d+) characters$/
    );

    if (match) {
        return t(
            'apiMessageTooLong',
            {
                max: match[1]
            }
        );
    }

    match = detail.match(
        /^Too many requests\. Retry in (\d+) seconds$/
    );

    if (match) {
        return t(
            'apiTooManyRequests',
            {
                seconds: match[1]
            }
        );
    }

    return detail;
}

export function getApiErrorMessage(
    error: unknown,
    fallbackKey: TranslationKey
): string {
    if (error instanceof ApiError) {
        const translated =
            translateApiDetail(
                extractDetail(error.data)
            );

        return translated ||
            t(fallbackKey);
    }

    if (error instanceof Error) {
        const translated =
            translateApiDetail(
                error.message
            );

        return translated ||
            t(fallbackKey);
    }

    return t(fallbackKey);
}