import {
    deleteMessage,
    editMessage
} from '$lib/api/messages';

import {
    reactToMessage
} from '$lib/api/reactions';

import {
    authState
} from '$lib/state/auth.svelte';

import {
    chatState
} from '$lib/state/chat.svelte';

import {
    composerState
} from '$lib/state/composer.svelte';

import type {
    Message
} from '$lib/types/message';

class MessageActions {
    editingMessageId =
        $state<number | null>(null);

    reply(
        message: Message
    ): void {
        composerState.setReply(
            message
        );

        document
            .getElementById(
                'message-input'
            )
            ?.focus();
    }

    startEdit(
        message: Message
    ): void {
        if (
            !message.id ||
            message.username !==
                authState.username ||
            message.content_type !==
                'text'
        ) {
            return;
        }

        this.editingMessageId =
            message.id;
    }

    cancelEdit(): void {
        this.editingMessageId =
            null;
    }

    async saveEdit(
        messageId: number,
        text: string
    ): Promise<boolean> {
        const clean = text.trim();

        if (!clean) {
            composerState.setStatus(
                'apiMessageEmpty',
                {},
                true
            );

            return false;
        }

        try {
            const result =
                await editMessage(
                    authState.token,
                    messageId,
                    clean
                );

            if (result.message) {
                chatState.replace(
                    result.message
                );
            }

            this.editingMessageId =
                null;

            return true;
        } catch (error) {
            composerState.setApiError(
                error,
                'cannotEditMessage'
            );

            return false;
        }
    }

    async delete(
        message: Message
    ): Promise<void> {
        if (
            !authState.isAdmin ||
            !message.id
        ) {
            return;
        }

        try {
            await deleteMessage(
                authState.token,
                message.id
            );

            chatState.remove(
                message.id
            );
        } catch (error) {
            composerState.setApiError(
                error,
                'cannotDeleteMessage'
            );
        }
    }

    async react(
        message: Message,
        emoji: string
    ): Promise<void> {
        if (!message.id) {
            return;
        }

        try {
            const result =
                await reactToMessage(
                    authState.token,
                    message.id,
                    emoji
                );

            chatState.updateReactions(
                result.message_id,
                result.reactions
            );
        } catch (error) {
            composerState.setApiError(
                error,
                'cannotReactMessage'
            );
        }
    }
}

export const messageActions =
    new MessageActions();