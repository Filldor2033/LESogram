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

    import Icon
        from '$components/common/Icon.svelte';

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

    let longPressMoved = false;

    let suppressClick =
        $state(false);

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

    function cancelLongPress() {
        if (longPressTimer != null) {
            clearTimeout(
                longPressTimer
            );

            longPressTimer = null;
        }
    }

    onDestroy(() => {
        cancelLongPress();
    });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
    class="msg"
    class:me={mine}
    class:other={!mine}
    class:suppress-click={suppressClick}
    data-message-id={message.id}
    oncontextmenu={(event) => {
        event.preventDefault();

        openContext(
            event.clientX,
            event.clientY
        );
    }}
    ontouchstart={(event) => {
        if (event.touches.length !== 1) {
            cancelLongPress();
            return;
        }

        const touch =
            event.touches[0];

        longPressMoved = false;
        cancelLongPress();

        longPressTimer =
            window.setTimeout(
                () => {
                    if (longPressMoved) {
                        return;
                    }

                    suppressClick = true;

                    openContext(
                        touch.clientX,
                        touch.clientY,
                        true
                    );
                },
                450
            );
    }}
    ontouchmove={() => {
        longPressMoved = true;
        cancelLongPress();
    }}
    ontouchend={(event) => {
        cancelLongPress();

        /*
         * A long-press that opened the menu
         * also fires a synthetic click —
         * swallow it so the menu does not
         * close immediately on mobile.
         */
        if (suppressClick) {
            event.preventDefault();
            suppressClick = false;
        }
    }}
    ontouchcancel={cancelLongPress}
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