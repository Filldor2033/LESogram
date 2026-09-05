import type {
    Message
} from '$lib/types/message';

class ContextMenuState {
    message =
        $state<Message | null>(null);

    x = $state(0);
    y = $state(0);

    touch = $state(false);

    get open(): boolean {
        return this.message !== null;
    }

    show(
        message: Message,
        x: number,
        y: number,
        touch = false
    ): void {
        this.message = message;

        this.x = x;
        this.y = y;

        this.touch = touch;

        if (touch && 'vibrate' in navigator) {
            try {
                navigator.vibrate(10);
            } catch {
                /* not supported */
            }
        }
    }

    close(): void {
        this.message = null;
        this.touch = false;
    }
}

export const contextMenuState =
    new ContextMenuState();
