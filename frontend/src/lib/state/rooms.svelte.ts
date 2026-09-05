import {
    createRoom as createRoomRequest,
    deleteRoom as deleteRoomRequest,
    getRooms,
    joinRoom as joinRoomRequest
} from '$lib/api/rooms';

import { authState } from '$lib/state/auth.svelte';

import type { Room } from '$lib/types/room';

export type OnlineFilter =
    | 'all'
    | 'online'
    | 'empty';

export type RoomSort =
    | 'name_asc'
    | 'name_desc'
    | 'online_desc'
    | 'online_asc'
    | 'creator_asc';

class RoomsState {
    items = $state<Room[]>([]);

    loading = $state(false);
    error = $state<string | null>(null);

    currentRoom = $state('');
    roomToken = $state('');

    roomSearch = $state('');
    creatorSearch = $state('');

    onlineFilter =
        $state<OnlineFilter>('all');

    sort =
        $state<RoomSort>('name_asc');

    collapsed = $state(false);

    get selected(): Room | undefined {
        return this.items.find(
            room =>
                room.name === this.currentRoom
        );
    }

    get filtered(): Room[] {
        const roomQuery =
            this.roomSearch
                .trim()
                .toLowerCase();

        const creatorQuery =
            this.creatorSearch
                .trim()
                .toLowerCase();

        let rooms = [...this.items];

        if (roomQuery) {
            rooms = rooms.filter(room =>
                room.name
                    .toLowerCase()
                    .includes(roomQuery)
            );
        }

        if (creatorQuery) {
            rooms = rooms.filter(room =>
                room.created_by
                    .toLowerCase()
                    .includes(creatorQuery)
            );
        }

        if (this.onlineFilter === 'online') {
            rooms = rooms.filter(
                room => room.online > 0
            );
        }

        if (this.onlineFilter === 'empty') {
            rooms = rooms.filter(
                room => room.online === 0
            );
        }

        rooms.sort((a, b) => {
            switch (this.sort) {
                case 'name_asc':
                    return a.name.localeCompare(
                        b.name
                    );

                case 'name_desc':
                    return b.name.localeCompare(
                        a.name
                    );

                case 'online_desc':
                    return b.online - a.online;

                case 'online_asc':
                    return a.online - b.online;

                case 'creator_asc':
                    return a.created_by.localeCompare(
                        b.created_by
                    );
            }
        });

        return rooms;
    }

    async load(): Promise<void> {
        if (!authState.token) {
            return;
        }

        this.loading = true;
        this.error = null;

        try {
            this.items =
                await getRooms(authState.token);
        } catch (error) {
            this.error =
                'Не удалось загрузить комнаты';

            throw error;
        } finally {
            this.loading = false;
        }
    }

    async create(
        name: string,
        password: string
    ): Promise<void> {
        name = name.trim();
        password = password.trim();

        if (!name || !password) {
            throw new Error(
                'Название и пароль обязательны'
            );
        }

        this.error = null;

        await createRoomRequest(
            authState.token,
            {
                name,
                password
            }
        );

        await this.load();
    }

    async join(
        room: Room,
        password: string
    ): Promise<string> {
        password = password.trim();

        if (
            !password &&
            !authState.isAdmin
        ) {
            throw new Error(
                'ROOM_PASSWORD_REQUIRED'
            );
        }

        const result =
            await joinRoomRequest(
                authState.token,
                {
                    room: room.name,
                    password
                }
            );

        this.currentRoom =
            room.name;

        this.roomToken =
            result.room_token;

        return result.room_token;
    }

    async delete(
        room: Room
    ): Promise<void> {
        await deleteRoomRequest(
            authState.token,
            room.name
        );

        if (
            this.currentRoom === room.name
        ) {
            this.leave();
        }

        await this.load();
    }

    leave(): void {
        this.currentRoom = '';
        this.roomToken = '';
    }

    resetFilters(): void {
        this.roomSearch = '';
        this.creatorSearch = '';
        this.onlineFilter = 'all';
        this.sort = 'name_asc';
    }

    clear(): void {
        this.items = [];
        this.resetFilters();
        this.leave();
        this.error = null;
    }
}

export const roomsState =
    new RoomsState();