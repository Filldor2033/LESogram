class UiState {
    chatFullscreen = $state(false);

    setChatFullscreen(
        value: boolean
    ): void {
        this.chatFullscreen = value;

        document.body.classList.toggle(
            'chat-fullscreen-mode',
            value
        );
    }

    toggleChatFullscreen(): void {
        this.setChatFullscreen(
            !this.chatFullscreen
        );
    }
}

export const uiState =
    new UiState();