import type {
    Message,
    MessageReactions
} from './message';

export interface PingEvent {
    type: 'ping';
}

export interface TypingEvent {
    type: 'typing';

    username?: string;
    is_typing: boolean;

    room?: string;
}

export interface MentionEvent {
    type: 'mention';

    from: string;
    text: string;
    room: string;
}

export interface MessageEditedEvent {
    type: 'message_edited';
    message: Message;
}

export interface MessageDeletedEvent {
    type: 'message_deleted';
    message_id: number;
}

export interface MessageReactionsUpdatedEvent {
    type: 'message_reactions_updated';

    message_id: number;
    reactions: MessageReactions;
}

export type ServerEvent =
    | PingEvent
    | TypingEvent
    | MentionEvent
    | MessageEditedEvent
    | MessageDeletedEvent
    | MessageReactionsUpdatedEvent
    | Message;

export interface SendMessagePayload {
    text: string;
    reply_to_id: number | null;
}

export interface SendTypingPayload {
    type: 'typing';
    is_typing: boolean;
}

export interface PongPayload {
    type: 'pong';
    timestamp: string;
}

export type ClientEvent =
    | SendMessagePayload
    | SendTypingPayload
    | PongPayload;