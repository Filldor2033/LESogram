export type MessageContentType =
    | 'text'
    | 'image'
    | 'gif'
    | 'video'
    | 'file'
    | 'voice';

export type SystemEvent =
    | 'joined'
    | 'left'
    | 'room_deleted'
    | 'rate_limited';

export type MessageReactions =
    Record<string, string[]>;

export type MessageKind =
    | 'message'
    | 'system';

export interface Message {
    id?: number;

    type?: MessageKind;

    username?: string;
    text?: string;
    timestamp?: string;

    content_type?: MessageContentType;

    reply_to_id?: number | null;

    is_edited?: boolean;

    reactions?: MessageReactions;

    media_url?: string;
    file_name?: string;
    file_size?: number;
    mime_type?: string;
    voice_duration?: number;

    system_event?: SystemEvent;
    system_actor?: string;

    room?: string;
}

export interface MessagesPage {
    messages: Message[];
    next_before_id: number | null;
    has_more: boolean;
}