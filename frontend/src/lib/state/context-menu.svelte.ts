import type {
    Message
} from '$lib/types/message';

class ContextMenuState {
    message =
        $state<Message | null>(null);

    x = $state(0);
    y = $state(0);

    get open(): boolean {
        return this.message !== null;
    }

    show(
        message: Message,
        x: number,
        y: number
    ): void {
        this.message = message;

        this.x = x;
        this.y = y;
    }

    close(): void {
        this.message = null;
    }
}

export const contextMenuState =
    new ContextMenuState();