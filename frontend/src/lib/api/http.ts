const API_PREFIX = '/api';

export class ApiError extends Error {
    constructor(
        public readonly status: number,
        public readonly data: unknown
    ) {
        super(`HTTP ${status}`);
        this.name = 'ApiError';
    }
}

function buildHeaders(
    headers?: HeadersInit
): Headers {
    const result = new Headers(headers);

    if (!result.has('Accept')) {
        result.set('Accept', 'application/json');
    }

    return result;
}

export async function request<T>(
    path: string,
    init: RequestInit = {}
): Promise<T> {
    const response = await fetch(
        `${API_PREFIX}${path}`,
        {
            ...init,
            headers: buildHeaders(init.headers)
        }
    );

    if (!response.ok) {
        const contentType =
            response.headers.get('content-type');

        let data: unknown;

        if (contentType?.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        throw new ApiError(
            response.status,
            data
        );
    }

    if (response.status === 204) {
        return undefined as T;
    }

    const contentType =
        response.headers.get('content-type');

    if (!contentType?.includes('application/json')) {
        return undefined as T;
    }

    return response.json() as Promise<T>;
}

export function jsonRequest<T>(
    path: string,
    method: string,
    body?: unknown,
    token?: string
): Promise<T> {
    const headers = new Headers({
        'Content-Type': 'application/json'
    });

    if (token) {
        headers.set(
            'Authorization',
            `Bearer ${token}`
        );
    }

    return request<T>(path, {
        method,
        headers,
        body:
            body === undefined
                ? undefined
                : JSON.stringify(body)
    });
}