import {
    jsonRequest,
    request
} from '$lib/api/http';

import type {
    AuthResponse,
    CurrentUser,
    LoginRequest,
    RegisterRequest
} from '$lib/types/auth';

export function login(
    data: LoginRequest
): Promise<AuthResponse> {
    return jsonRequest<AuthResponse>(
        '/login',
        'POST',
        data
    );
}

export function register(
    data: RegisterRequest
): Promise<AuthResponse> {
    return jsonRequest<AuthResponse>(
        '/register',
        'POST',
        data
    );
}

export function getCurrentUser(
    token: string
): Promise<CurrentUser> {
    return request<CurrentUser>('/me', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
}