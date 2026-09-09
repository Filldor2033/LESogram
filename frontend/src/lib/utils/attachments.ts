import { API_BASE } from '$lib/api/base';

export function resolveAttachmentUrl(
    mediaUrl: string | undefined,
    roomToken: string
): string {
    if (!mediaUrl) {
        return '';
    }

    /*
     * Native app: media URLs come back from the API as absolute
     * server paths (/attachments/.., /api/avatars/..) — prepend the
     * API base. Web: same origin, keep as is.
     */
    const absolute = API_BASE !== '' ? `${API_BASE}${mediaUrl}` : mediaUrl;

    if (!roomToken) {
        return absolute;
    }

    const separator =
        mediaUrl.includes('?')
            ? '&'
            : '?';

    return (
        absolute +
        separator +
        'room_token=' +
        encodeURIComponent(roomToken)
    );
}