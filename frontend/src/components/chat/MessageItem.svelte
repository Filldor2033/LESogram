<script lang="ts">
    import {
        onDestroy
    } from 'svelte';

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

    let longPressTimer:
        number | null = null;

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
        y: number
    ) {
        if (!message.id) {
            return;
        }

        contextMenuState.show(
            message,
            x,
            y
        );
    }

    function cancelLongPress() {
        if (longPressTimer != null) {
            clearTimeout(
                longPressTimer
            );

            longPressTimer = null;
        }
    }

    onDestroy(cancelLongPress);
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
    class="msg"
    class:me={mine}
    class:other={!mine}
    data-message-id={message.id}
    oncontextmenu={(event) => {
        event.preventDefault();

        openContext(
            event.clientX,
            event.clientY
        );
    }}
    ontouchstart={(event) => {
        const touch =
            event.touches[0];

        cancelLongPress();

        longPressTimer =
            window.setTimeout(
                () => {
                    openContext(
                        touch.clientX,
                        touch.clientY
                    );
                },
                550
            );
    }}
    ontouchend={cancelLongPress}
    ontouchmove={cancelLongPress}
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