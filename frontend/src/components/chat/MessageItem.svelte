<script lang="ts">
    import type {
        Message
    } from '$lib/types/message';

    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        contextMenuState
    } from '$lib/state/context-menu.svelte';

    import {
        messageActions
    } from '$lib/services/message-actions.svelte';

    import {
        formatTime
    } from '$lib/utils/time';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import MessageText
        from './MessageText.svelte';

    import MessageReply
        from './MessageReply.svelte';

    import MessageAttachment
        from './MessageAttachment.svelte';

    import MessageReactions
        from './MessageReactions.svelte';

    import MessageEditor
        from './MessageEditor.svelte';

    let {
        message
    }: {
        message: Message;
    } = $props();

    /*
     * Touch devices (no hover + coarse pointer, e.g.
     * phones/tablets) open the context menu with a plain
     * tap; desktop keeps right-click.
     */
    const isTouchDevice =
        typeof window !== 'undefined' &&
        window.matchMedia(
            '(hover: none) and (pointer: coarse)'
        ).matches;

    let mine = $derived(
        message.username ===
            authState.username
    );

    let editing = $derived(
        message.id != null &&
        messageActions
            .editingMessageId ===
            message.id
    );

    function openContext(
        x: number,
        y: number,
        touch = false
    ) {
        if (!message.id) {
            return;
        }

        contextMenuState.show(
            message,
            x,
            y,
            touch
        );
    }

    function handleClick(
        event: MouseEvent
    ) {
        if (!isTouchDevice) {
            return;
        }

        /*
         * Taps on links, buttons and media inside the
         * message keep their native behaviour.
         */
        const target = event.target as HTMLElement;

        if (
            target.closest(
                'a, button, video, input, textarea'
            )
        ) {
            return;
        }

        if (contextMenuState.open) {
            return;
        }

        /*
         * Stop the very same click from bubbling to the
         * window-level listener that closes the menu.
         */
        event.stopPropagation();

        openContext(
            event.clientX,
            event.clientY,
            true
        );
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
    class="msg"
    class:me={mine}
    class:other={!mine}
    data-message-id={message.id}
    oncontextmenu={(event) => {
        if (isTouchDevice) {
            return;
        }

        event.preventDefault();

        openContext(
            event.clientX,
            event.clientY
        );
    }}
    onclick={handleClick}
>
    {#if message.reply_to_id}
        <MessageReply
            replyToId={
                message.reply_to_id
            }
        />
    {/if}

    <div class="msg-username">
        {message.username}
    </div>

    <MessageAttachment
        {message}
    />

    {#if editing}
        <MessageEditor
            {message}
        />

    {:else if message.text?.trim()}
        <MessageText
            text={message.text}
        />
    {/if}

    <MessageReactions
        {message}
    />

    <div class="meta">
        {formatTime(
            message.timestamp
        )}

        {#if message.is_edited}
            · {t('edited')}
        {/if}
    </div>
</div>
