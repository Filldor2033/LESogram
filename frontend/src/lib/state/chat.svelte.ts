import {
    getMessages
} from '$lib/api/messages';

import type {
    Message,
    MessageReactions
} from '$lib/types/message';

export type RealtimeState =
    | 'idle'
    | 'connecting'
    | 'open'
    | 'closed';

class ChatState {
    messages = $state<Message[]>([]);

    room = $state('');
    roomToken = $state('');

    loading = $state(false);
    loadingOlder = $state(false);

    nextBeforeId =
        $state<number | null>(null);

    hasMore = $state(true);

    realtime =
        $state<RealtimeState>('idle');

    /**
     * Используется MessageList для автоматического
     * скролла вниз после нового сообщения.
     */
    bottomRevision = $state(0);

    typingUsers =
        $state<string[]>([]);

    private typingTimers =
        new Map<string, number>();

    get empty(): boolean {
        return this.messages.length === 0;
    }

    get active(): boolean {
        return Boolean(
            this.room &&
            this.roomToken
        );
    }

    getMessage(
        id: number
    ): Message | undefined {
        return this.messages.find(
            message => message.id === id
        );
    }

    async open(
        room: string,
        roomToken: string
    ): Promise<void> {
        this.reset();

        this.room = room;
        this.roomToken = roomToken;

        await this.loadInitial();
    }

    async loadInitial(): Promise<void> {
        if (!this.active || this.loading) {
            return;
        }

        this.loading = true;

        try {
            const page =
                await getMessages(
                    this.room,
                    this.roomToken
                );

            this.messages =
                page.messages ?? [];

            this.nextBeforeId =
                page.next_before_id;

            this.hasMore =
                Boolean(page.has_more);

            ++this.bottomRevision;
        } finally {
            this.loading = false;
        }
    }

    async loadOlder(): Promise<boolean> {
        if (
            !this.active ||
            !this.hasMore ||
            this.loadingOlder
        ) {
            return false;
        }

        this.loadingOlder = true;

        try {
            const page =
                await getMessages(
                    this.room,
                    this.roomToken,
                    this.nextBeforeId
                );

            const older =
                page.messages ?? [];

            /*
             * Старые сообщения добавляем В НАЧАЛО.
             */
            this.messages = [
                ...older,
                ...this.messages
            ];

            this.nextBeforeId =
                page.next_before_id;

            this.hasMore =
                Boolean(page.has_more);

            return older.length > 0;
        } finally {
            this.loadingOlder = false;
        }
    }

    append(
        message: Message
    ): void {
        /*
         * Защита от дубликатов.
         */
        if (
            message.id != null &&
            this.getMessage(message.id)
        ) {
            this.replace(message);
            return;
        }

        this.messages.push(message);

        ++this.bottomRevision;
    }

    replace(
        message: Message
    ): void {
        if (message.id == null) {
            return;
        }

        const index =
            this.messages.findIndex(
                current =>
                    current.id === message.id
            );

        if (index === -1) {
            return;
        }

        this.messages[index] = message;
    }

    remove(
        messageId: number
    ): void {
        const index =
            this.messages.findIndex(
                message =>
                    message.id === messageId
            );

        if (index !== -1) {
            this.messages.splice(
                index,
                1
            );
        }
    }

    updateReactions(
        messageId: number,
        reactions: MessageReactions
    ): void {
        const message =
            this.getMessage(messageId);

        if (!message) {
            return;
        }

        message.reactions =
            reactions ?? {};
    }

    setTyping(
        username: string,
        typing: boolean
    ): void {
        const oldTimer =
            this.typingTimers.get(
                username
            );

        if (oldTimer != null) {
            window.clearTimeout(
                oldTimer
            );

            this.typingTimers.delete(
                username
            );
        }

        if (!typing) {
            this.typingUsers =
                this.typingUsers.filter(
                    user =>
                        user !== username
                );

            return;
        }

        if (
            !this.typingUsers.includes(
                username
            )
        ) {
            this.typingUsers.push(
                username
            );
        }

        /*
         * Старый frontend держал typing примерно 2.5 секунды.
         */
        const timer =
            window.setTimeout(
                () => {
                    this.typingUsers =
                        this.typingUsers.filter(
                            user =>
                                user !==
                                username
                        );

                    this.typingTimers.delete(
                        username
                    );
                },
                2500
            );

        this.typingTimers.set(
            username,
            timer
        );
    }

    clearTyping(): void {
        for (
            const timer
            of this.typingTimers.values()
        ) {
            window.clearTimeout(timer);
        }

        this.typingTimers.clear();
        this.typingUsers = [];
    }

    reset(): void {
        this.clearTyping();

        this.messages = [];

        this.room = '';
        this.roomToken = '';

        this.nextBeforeId = null;
        this.hasMore = true;

        this.loading = false;
        this.loadingOlder = false;

        this.realtime = 'idle';
    }
}

export const chatState =
    new ChatState();