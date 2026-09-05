import {
    jsonRequest,
    request
} from '$lib/api/http';

import type {
    CreateRoomRequest,
    JoinRoomRequest,
    JoinRoomResponse,
    Room,
    RoomUsersResponse
} from '$lib/types/room';

export function getRooms(
    token: string
): Promise<Room[]> {
    return request<Room[]>('/rooms', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function createRoom(
    token: string,
    data: CreateRoomRequest
): Promise<unknown> {
    return jsonRequest(
        '/rooms',
        'POST',
        data,
        token
    );
}

export function joinRoom(
    token: string,
    data: JoinRoomRequest
): Promise<JoinRoomResponse> {
    return jsonRequest<JoinRoomResponse>(
        '/rooms/join',
        'POST',
        data,
        token
    );
}

export function deleteRoom(
    token: string,
    roomName: string
): Promise<void> {
    return request<void>(
        `/rooms/${encodeURIComponent(roomName)}`,
        {
            method: 'DELETE',

            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );
}

export function getRoomUsers(
    room: string,
    roomToken: string
): Promise<RoomUsersResponse> {
    return request<RoomUsersResponse>(
        `/rooms/${encodeURIComponent(room)}` +
        `/users?room_token=${encodeURIComponent(roomToken)}`
    );
}