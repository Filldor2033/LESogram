import {
    t
} from '$lib/i18n/i18n.svelte';

import {
    isNativeApp
} from '$lib/utils/platform';

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
        /*
         * The Capacitor WebView has no DOM Notification API, but
         * the @capacitor/local-notifications plugin provides native
         * ones — so the feature is supported in the app too.
         */
        if (isNativeApp()) {
            return true;
        }

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

        if (isNativeApp()) {
            /*
             * Native path: request through the plugin. Android 13+
             * additionally needs the runtime POST_NOTIFICATIONS
             * grant MainActivity asks for on launch.
             */
            const cap = (
                window as unknown as {
                    Capacitor?: {
                        Plugins?: {
                            LocalNotifications?: {
                                requestPermissions: () => Promise<{
                                    display?: string;
                                }>;
                            };
                        };
                        isPluginAvailable?: (name: string) => boolean;
                    };
                }
            ).Capacitor;

            const plugin =
                cap?.Plugins?.LocalNotifications;

            if (!plugin) {
                return 'unsupported';
            }

            try {
                const status =
                    await plugin.requestPermissions();

                if (status.display !== 'granted') {
                    this.enabled = false;

                    localStorage.setItem(
                        'notifications_enabled',
                        '0'
                    );

                    return 'denied';
                }
            } catch {
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
        if (isNativeApp()) {
            // The plugin path has no DOM permission to check.
            return this.enabled && document.hidden;
        }

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

        if (isNativeApp()) {
            const cap = (
                window as unknown as {
                    Capacitor?: {
                        Plugins?: {
                            LocalNotifications?: {
                                show: (options: {
                                    title: string;
                                    body: string;
                                    id: number;
                                }) => Promise<void>;
                            };
                        };
                    };
                }
            ).Capacitor;

            cap?.Plugins?.LocalNotifications?.show({
                title: t(
                    'newMessageTitle',
                    { room }
                ),
                body,
                id: message.id ??
                    Math.floor(
                        Date.now() / 1000
                    )
            });

            return;
        }

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