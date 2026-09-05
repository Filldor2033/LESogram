<script lang="ts">
    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        getReplyPreview
    } from '$lib/utils/messages';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    let {
        replyToId
    }: {
        replyToId: number;
    } = $props();

    let replied = $derived(
        chatState.getMessage(
            replyToId
        )
    );

    function scrollToReply() {
        document
            .querySelector<HTMLElement>(
                `.msg[data-message-id="${replyToId}"]`
            )
            ?.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
    }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
    class="msg-reply"
    onclick={scrollToReply}
>
    <div class="msg-reply-author">
        {replied?.username ||
            t('reply')}
    </div>

    <div class="msg-reply-text">
        {replied
            ? getReplyPreview(replied)
            : `#${replyToId}`}
    </div>
</div>