export function resolveAttachmentUrl(
    mediaUrl: string | undefined,
    roomToken: string
): string {
    if (!mediaUrl) {
        return '';
    }

    if (!roomToken) {
        return mediaUrl;
    }

    const separator =
        mediaUrl.includes('?')
            ? '&'
            : '?';

    return (
        mediaUrl +
        separator +
        'room_token=' +
        encodeURIComponent(roomToken)
    );
}