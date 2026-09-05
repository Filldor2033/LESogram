import {
    jsonRequest
} from '$lib/api/http';

import type {
    MessageReactions
} from '$lib/types/message';

export interface ReactionResponse {
    message_id: number;
    reactions: MessageReactions;
}

export function reactToMessage(
    token: string,
    messageId: number,
    emoji: string
): Promise<ReactionResponse> {
    return jsonRequest<ReactionResponse>(
        `/messages/${encodeURIComponent(messageId)}/reactions`,
        'POST',
        { emoji },
        token
    );
}