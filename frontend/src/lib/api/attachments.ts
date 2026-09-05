import {
    request
} from '$lib/api/http';

import type {
    Message
} from '$lib/types/message';

export function sendAttachment(
    token: string,
    room: string,
    formData: FormData
): Promise<Message> {
    return request<Message>(
        `/rooms/${encodeURIComponent(room)}/attachments`,
        {
            method: 'POST',

            headers: {
                Authorization:
                    `Bearer ${token}`
            },

            body: formData
        }
    );
}