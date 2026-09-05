export interface Room {
    name: string;
    created_by: string;
    online: number;
}

export interface CreateRoomRequest {
    name: string;
    password: string;
}

export interface JoinRoomRequest {
    room: string;
    password: string;
}

export interface JoinRoomResponse {
    room_token: string;
}

export interface RoomUser {
    username: string;
    is_admin: boolean;
}

export type RawRoomUser =
    | string
    | {
        username: string;
        is_admin?: boolean;
    };

export interface RoomUsersResponse {
    count: number;
    users: RawRoomUser[];
}