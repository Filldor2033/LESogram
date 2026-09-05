import {
    t
} from '$lib/i18n/i18n.svelte';

import {
    authState
} from '$lib/state/auth.svelte';

import type {
    Message
} from '$lib/types/message';

export type NotificationToggleResult =
    | 'enabled'
    | 'disabled'
    | 'unsupported'
    | 'denied';

class NotificationsState {
    enabled = $state(
        typeof localStorage !==
            'undefined' &&
        localStorage.getItem(
            'notifications_enabled'
        ) === '1'
    );

    get supported(): boolean {
        return (
            typeof window !== 'undefined' &&
            'Notification' in window
        );
    }

    async toggle():
        Promise<NotificationToggleResult> {
        if (!this.supported) {
            return 'unsupported';
        }

        if (this.enabled) {
            this.enabled = false;

            localStorage.setItem(
                'notifications_enabled',
                '0'
            );

            return 'disabled';
        }

        const permission =
            await Notification
                .requestPermission();

        if (permission !== 'granted') {
            this.enabled = false;

            localStorage.setItem(
                'notifications_enabled',
                '0'
            );

            return 'denied';
        }

        this.enabled = true;

        localStorage.setItem(
            'notifications_enabled',
            '1'
        );

        return 'enabled';
    }

    get allowed(): boolean {
        return (
            this.enabled &&
            this.supported &&
            Notification.permission ===
                'granted' &&
            document.hidden
        );
    }

    notifyMessage(
        message: Message,
        currentRoom: string
    ): void {
        if (!this.allowed) {
            return;
        }

        if (
            message.username ===
            authState.username
        ) {
            return;
        }

        const room =
            message.room ||
            currentRoom;

        const body =
            message.text ||
            message.file_name ||
            t('attachmentLabel');

        new Notification(
            t(
                'newMessageTitle',
                { room }
            ),
            {
                body,

                tag:
                    `room-${room}-` +
                    `${message.id ??
                        Date.now()}`
            }
        );
    }

    notifyMention(
        from: string,
        text: string
    ): void {
        if (!this.allowed) {
            return;
        }

        new Notification(
            t('mentionTitle'),
            {
                body: `${from}: ${text}`
            }
        );
    }
}

export const notificationsState =
    new NotificationsState();