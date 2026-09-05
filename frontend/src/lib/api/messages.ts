import {
    jsonRequest,
    request
} from '$lib/api/http';

import type {
    Message,
    MessagesPage
} from '$lib/types/message';

export function getMessages(
    room: string,
    roomToken: string,
    beforeId?: number | null
): Promise<MessagesPage> {
    const params = new URLSearchParams({
        room_token: roomToken
    });

    if (beforeId != null) {
        params.set(
            'before_id',
            String(beforeId)
        );
    }

    return request<MessagesPage>(
        `/messages/${encodeURIComponent(room)}?${params}`
    );
}

export function editMessage(
    token: string,
    messageId: number,
    text: string
): Promise<{ message: Message }> {
    return jsonRequest<{ message: Message }>(
        `/messages/${encodeURIComponent(messageId)}`,
        'PATCH',
        { text },
        token
    );
}

export function deleteMessage(
    token: string,
    messageId: number
): Promise<void> {
    return request<void>(
        `/messages/${encodeURIComponent(messageId)}`,
        {
            method: 'DELETE',

            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );
}