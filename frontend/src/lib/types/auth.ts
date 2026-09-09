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
    display_name?: string | null;
    bio?: string | null;
    avatar_url?: string | null;
    created_at?: string | null;
}

export interface PublicProfile {
    username: string;
    display_name?: string | null;
    bio?: string | null;
    avatar_url?: string | null;
    is_admin: boolean;
}

export interface UserStats {
    total_messages: number;
    messages_by_type: Record<string, number>;
    rooms_active_in: number;
    first_message_at?: string | null;
    recent_messages: number;
}

export interface AdminUser {
    username: string;
    display_name?: string | null;
    bio?: string | null;
    avatar_url?: string | null;
    is_admin: boolean;
    created_at?: string | null;
    message_count: number;
}

export interface AdminRoom {
    name: string;
    created_by: string;
    created_at?: string | null;
    message_count: number;
}
