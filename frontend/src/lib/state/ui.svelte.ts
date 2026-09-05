class UiState {
    chatFullscreen = $state(false);

    fsSidebarHidden = $state(false);

    /*
     * Mobile (<= 900px) switches between two screens
     * instead of stacking them: the rooms list and the
     * chat. 'chat' is selected automatically when a room
     * is opened.
     */
    mobileView = $state<
        'rooms' | 'chat'
    >('rooms');

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

    toggleFsSidebar(): void {
        this.fsSidebarHidden =
            !this.fsSidebarHidden;

        document.body.classList.toggle(
            'fs-sidebar-hidden',
            this.fsSidebarHidden
        );
    }

    showMobileRooms(): void {
        this.mobileView = 'rooms';
    }

    showMobileChat(): void {
        this.mobileView = 'chat';
    }
}

export const uiState =
    new UiState();
