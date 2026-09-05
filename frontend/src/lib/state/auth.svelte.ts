import {
    getCurrentUser,
    login as loginRequest,
    register as registerRequest
} from '$lib/api/auth';

import type {
    LoginRequest,
    RegisterRequest
} from '$lib/types/auth';

const TOKEN_KEY = 'token';
const USERNAME_KEY = 'username';
const ADMIN_KEY = 'is_admin';

class AuthState {
    token = $state('');
    username = $state('');
    isAdmin = $state(false);

    loading = $state(false);
    initialized = $state(false);

    error = $state<string | null>(null);

    get authenticated(): boolean {
        return this.token.length > 0;
    }

    async initialize(): Promise<void> {
        const token =
            localStorage.getItem(TOKEN_KEY);

        if (!token) {
            this.initialized = true;
            return;
        }

        this.token = token;
        this.loading = true;

        try {
            const user =
                await getCurrentUser(token);

            this.username = user.username;
            this.isAdmin = user.is_admin;

            this.persist();
        } catch {
            this.clearSession();
        } finally {
            this.loading = false;
            this.initialized = true;
        }
    }

    async login(
        credentials: LoginRequest
    ): Promise<void> {
        this.loading = true;
        this.error = null;

        try {
            const result =
                await loginRequest(credentials);

            this.token = result.access_token;

            await this.loadUser();

            this.persist();
        } catch (error) {
            this.clearSession();

            this.error =
                'Не удалось войти';

            throw error;
        } finally {
            this.loading = false;
        }
    }

    async register(
        data: RegisterRequest
    ): Promise<void> {
        this.loading = true;
        this.error = null;

        try {
            const result =
                await registerRequest(data);

            this.token = result.access_token;

            await this.loadUser();

            this.persist();
        } catch (error) {
            this.clearSession();

            this.error =
                'Не удалось зарегистрироваться';

            throw error;
        } finally {
            this.loading = false;
        }
    }

    logout(): void {
        this.clearSession();
    }

    private async loadUser(): Promise<void> {
        const user =
            await getCurrentUser(this.token);

        this.username = user.username;
        this.isAdmin = user.is_admin;
    }

    private persist(): void {
        localStorage.setItem(
            TOKEN_KEY,
            this.token
        );

        localStorage.setItem(
            USERNAME_KEY,
            this.username
        );

        localStorage.setItem(
            ADMIN_KEY,
            this.isAdmin ? '1' : '0'
        );
    }

    private clearSession(): void {
        this.token = '';
        this.username = '';
        this.isAdmin = false;

        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USERNAME_KEY);
        localStorage.removeItem(ADMIN_KEY);
    }
}

export const authState = new AuthState();