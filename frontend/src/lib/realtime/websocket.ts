import type {
    ClientEvent,
    ServerEvent
} from '$lib/types/websocket';

export interface RealtimeCallbacks {
    onEvent:
        (event: ServerEvent) =>
            void | Promise<void>;

    onOpen?: () => void;
    onClose?: () => void;
}

let socket: WebSocket | null = null;

export function connectRealtime(
    room: string,
    roomToken: string,
    callbacks: RealtimeCallbacks
): void {
    disconnectRealtime();

    const protocol =
        location.protocol === 'https:'
            ? 'wss'
            : 'ws';

    const url =
        `${protocol}://${location.host}` +
        `/ws/${encodeURIComponent(room)}` +
        `?room_token=${encodeURIComponent(roomToken)}`;

    const current =
        new WebSocket(url);

    socket = current;

    current.addEventListener(
        'open',
        () => {
            if (socket !== current) {
                return;
            }

            callbacks.onOpen?.();
        }
    );

    current.addEventListener(
        'message',
        async event => {
            if (socket !== current) {
                return;
            }

            let payload: ServerEvent;

            try {
                payload =
                    JSON.parse(event.data);
            } catch {
                return;
            }

            /*
             * Старый backend использует ping/pong.
             */
            if (payload.type === 'ping') {
                sendRealtime({
                    type: 'pong',
                    timestamp:
                        new Date()
                            .toISOString()
                });

                return;
            }

            await callbacks.onEvent(
                payload
            );
        }
    );

    current.addEventListener(
        'close',
        () => {
            if (socket !== current) {
                return;
            }

            socket = null;

            callbacks.onClose?.();
        }
    );
}

export function disconnectRealtime(): void {
    const current = socket;

    socket = null;

    current?.close();
}

export function sendRealtime(
    payload: ClientEvent
): boolean {
    if (
        !socket ||
        socket.readyState !==
            WebSocket.OPEN
    ) {
        return false;
    }

    socket.send(
        JSON.stringify(payload)
    );

    return true;
}

export function realtimeIsOpen(): boolean {
    return (
        socket?.readyState ===
        WebSocket.OPEN
    );
}