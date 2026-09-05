export interface LoginRequest {
    username: string;
    password: string;
}

export interface RegisterRequest {
    username: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
}

export interface CurrentUser {
    username: string;
    is_admin: boolean;
}