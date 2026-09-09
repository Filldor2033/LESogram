import {
    jsonRequest,
    request
} from '$lib/api/http';

import type {
    AdminRoom,
    AdminUser,
    PublicProfile,
    UserStats
} from '$lib/types/auth';

export function getMyProfile(
    token: string
): Promise<PublicProfile & { created_at?: string | null }> {
    return request('/me', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function updateMyProfile(
    token: string,
    data: { display_name?: string | null; bio?: string | null }
): Promise<PublicProfile & { created_at?: string | null }> {
    return jsonRequest('/me', 'PATCH', data, token);
}

export function getMyStats(
    token: string
): Promise<UserStats> {
    return request('/me/stats', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function changeMyPassword(
    token: string,
    data: { current_password: string; new_password: string }
): Promise<{ ok: boolean }> {
    return jsonRequest('/me/password', 'POST', data, token);
}

export function getPublicProfile(
    token: string,
    username: string
): Promise<PublicProfile> {
    return request(
        `/users/${encodeURIComponent(username)}/profile`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );
}

export function uploadAvatar(
    token: string,
    file: File
): Promise<{ avatar_url: string }> {
    const form = new FormData();
    form.append('file', file);

    return request('/me/avatar', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}`
        },
        body: form
    });
}

export function deleteAvatar(
    token: string
): Promise<{ ok: boolean }> {
    return request('/me/avatar', {
        method: 'DELETE',
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function getAdminUsers(
    token: string
): Promise<{ users: AdminUser[] }> {
    return request('/admin/users', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function getAdminRooms(
    token: string
): Promise<{ rooms: AdminRoom[] }> {
    return request('/admin/rooms', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}

export function setAdminRole(
    token: string,
    username: string,
    isAdmin: boolean
): Promise<{ username: string; is_admin: boolean }> {
    const form = new FormData();
    form.append('is_admin', isAdmin ? 'true' : 'false');

    return request(
        `/admin/users/${encodeURIComponent(username)}/role`,
        {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: form
        }
    );
}
