import {
    connectRealtime,
    disconnectRealtime
} from '$lib/realtime/websocket';

import {
    chatState
} from '$lib/state/chat.svelte';

import {
    roomsState
} from '$lib/state/rooms.svelte';

import {
    authState
} from '$lib/state/auth.svelte';

import type {
    Message
} from '$lib/types/message';

import type {
    ServerEvent
} from '$lib/types/websocket';

import {
    notificationsState
} from '$lib/state/notifications.svelte';

import {
    roomUsersState
} from '$lib/state/room-users.svelte';

import {
    composerState
} from '$lib/state/composer.svelte';

import {
    uiState
} from '$lib/state/ui.svelte';

async function handleRealtimeEvent(
    event: ServerEvent
): Promise<void> {
    if (
        'room' in event &&
        event.room &&
        event.room !== chatState.room
    ) {
        return;
    }

    switch (event.type) {
        case 'typing': {
            const username =
                event.username;

            if (
                !username ||
                username ===
                    authState.username
            ) {
                return;
            }

            chatState.setTyping(
                username,
                event.is_typing
            );

            return;
        }

        case 'mention': {
            notificationsState
                .notifyMention(
                    event.from,
                    event.text
                );

            composerState.setStatus(
                'mentionStatus',
                {
                    user:
                        event.from
                }
            );

            return;
        }

        case 'message_edited': {
            chatState.replace(
                event.message
            );

            return;
        }

        case 'message_deleted': {
            chatState.remove(
                event.message_id
            );

            return;
        }

        case 'message_reactions_updated': {
            chatState.updateReactions(
                event.message_id,
                event.reactions ??
                    {}
            );

            return;
        }
    }

    if (event.type === 'system') {
        if (
            event.system_event ===
                'room_deleted'
        ) {
            await handleRoomDeleted(
                event
            );

            return;
        }

        if (
            event.system_event ===
                'joined' ||
            event.system_event ===
                'left'
        ) {
            await roomUsersState
                .refresh(
                    chatState.room,
                    chatState.roomToken,
                    true
                );
        }

        chatState.append(event);

        return;
    }

    const message =
        event as Message;

    notificationsState
        .notifyMessage(
            message,
            chatState.room
        );

    chatState.append(
        message
    );

    /*
     * Старый frontend обновлял users popup
     * после нового сообщения.
     */
    if (roomUsersState.open) {
        await roomUsersState
            .refresh(
                chatState.room,
                chatState.roomToken,
                true
            );
    }
}

async function handleRoomDeleted(
    event: Message
): Promise<void> {
    disconnectRealtime();

    const deletedRoom =
        event.room ||
        roomsState.currentRoom;

    chatState.reset();
    roomsState.leave();

    /*
     * Mobile: the room is gone — back to the rooms screen.
     */
    uiState.showMobileRooms();

    /*
     * В следующем улучшении status тоже
     * оформим как semantic i18n message.
     */

    await roomsState.load();

    console.info(
        'Room deleted:',
        deletedRoom
    );
}

export async function openChat(
    room: string,
    roomToken: string
): Promise<void> {
    disconnectRealtime();

    composerState.reset();
    roomUsersState.clear();

    /*
     * Mobile: entering a room shows the chat screen.
     */
    uiState.showMobileChat();

    /*
     * 1. история
     */
    await chatState.open(
        room,
        roomToken
    );

    /*
     * 2. users для mentions
     */
    await roomUsersState.refresh(
        room,
        roomToken,
        true
    );

    /*
     * 3. realtime
     */
    chatState.realtime =
        'connecting';

    connectRealtime(
        room,
        roomToken,
        {
            onOpen() {
                chatState.realtime =
                    'open';

                composerState
                    .clearStatus();
            },

            onClose() {
                if (chatState.active) {
                    chatState.realtime =
                        'closed';
                }
            },

            onEvent:
                handleRealtimeEvent
        }
    );
}

export function closeChat(): void {
    disconnectRealtime();

    chatState.reset();
    composerState.reset();
    roomUsersState.clear();

    /*
     * Mobile: leaving a room returns to the rooms screen.
     */
    uiState.showMobileRooms();
}