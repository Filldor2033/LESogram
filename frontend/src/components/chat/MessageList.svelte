<script lang="ts">
    import {
        tick
    } from 'svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        contextMenuState
    } from '$lib/state/context-menu.svelte';

    import MessageItem
        from './MessageItem.svelte';

    import SystemMessage
        from './SystemMessage.svelte';

    let chatElement:
        HTMLDivElement;

    let dragging = $state(false);

    async function scrollToBottom() {
        await tick();

        if (!chatElement) {
            return;
        }

        chatElement.scrollTop =
            chatElement.scrollHeight;
    }

    async function handleScroll() {
        if (
            !chatElement ||
            chatElement.scrollTop >= 80 ||
            !chatState.hasMore ||
            chatState.loadingOlder
        ) {
            return;
        }

        const oldHeight =
            chatElement.scrollHeight;

        const oldTop =
            chatElement.scrollTop;

        const loaded =
            await chatState.loadOlder();

        if (!loaded) {
            return;
        }

        await tick();

        const newHeight =
            chatElement.scrollHeight;

        chatElement.scrollTop =
            newHeight -
            oldHeight +
            oldTop;
        
        contextMenuState.close();
    }

    $effect(() => {
        /*
         * Читаем revision, чтобы Svelte
         * зарегистрировал dependency.
         */
        chatState.bottomRevision;

        void scrollToBottom();
    });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
    id="chat"
    class="chat"
    class:drag-over={dragging}
    bind:this={chatElement}
    onscroll={handleScroll}

    ondragover={(event) => {
        event.preventDefault();

        if (chatState.active) {
            dragging = true;
        }
    }}

    ondragleave={() => {
        dragging = false;
    }}

    ondrop={(event) => {
        event.preventDefault();

        dragging = false;

        if (!chatState.active) {
            return;
        }

        const file =
            event.dataTransfer
                ?.files?.[0];

        if (file) {
            composerState
                .setPendingFile(file);
        }
    }}
>
    {#if chatState.loading}
        <div class="chat-empty">
            <div class="chat-empty-text">
                {t('cannotLoadMessages')
                    .replace(
                        t('cannotLoadMessages'),
                        ''
                    )}
            </div>
        </div>

    {:else if chatState.empty}
        <div class="chat-empty">
            <div class="chat-empty-title">
                {chatState.active
                    ? t('emptyNoMessagesTitle')
                    : t('emptyNoRoomTitle')}
            </div>

            <div class="chat-empty-text">
                {chatState.active
                    ? t('emptyNoMessagesText')
                    : t('emptyNoRoomText')}
            </div>
        </div>

    {:else}
        {#each chatState.messages as message}
            {#if message.type === 'system'}
                <SystemMessage
                    {message}
                />
            {:else}
                <MessageItem
                    {message}
                />
            {/if}
        {/each}
    {/if}
</div>