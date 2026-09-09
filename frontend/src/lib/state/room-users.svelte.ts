import {
    getRoomUsers
} from '$lib/api/rooms';

import type {
    RoomUser
} from '$lib/types/room';

class RoomUsersState {
    users = $state<RoomUser[]>([]);

    open = $state(false);
    loading = $state(false);

    error = $state<unknown>(null);

    async refresh(
        room: string,
        roomToken: string,
        silent = false
    ): Promise<void> {
        if (!room || !roomToken) {
            this.clear();
            return;
        }

        if (!silent) {
            this.loading = true;
        }

        this.error = null;

        try {
            const data =
                await getRoomUsers(
                    room,
                    roomToken
                );

            this.users =
                (data.users ?? [])
                    .map(user => {
                        if (
                            typeof user ===
                            'string'
                        ) {
                            return {
                                username: user,
                                is_admin: false
                            };
                        }

                        return {
                            username:
                                user.username,

                            is_admin:
                                Boolean(
                                    user.is_admin
                                ),

                            display_name:
                                user.display_name ??
                                null,

                            avatar_url:
                                user.avatar_url ??
                                null
                        };
                    });
        } catch (error) {
            this.error = error;
        } finally {
            this.loading = false;
        }
    }

    clear(): void {
        this.users = [];
        this.open = false;

        this.loading = false;
        this.error = null;
    }

    close(): void {
        this.open = false;
    }
}

export const roomUsersState =
    new RoomUsersState();