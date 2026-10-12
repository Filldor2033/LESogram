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
        const target = document.querySelector<HTMLElement>(
            `.msg[data-message-id="${replyToId}"]`
        );

        target?.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        /*
         * Flash the replied-to message: re-trigger the CSS
         * animation (restart it if a previous one is still
         * running). The class is removed on animationend.
         */
        if (target) {
            target.classList.remove('msg-flash');
            void target.offsetWidth; // force reflow to restart animation
            target.classList.add('msg-flash');

            const cleanup = () => {
                target.classList.remove('msg-flash');
                target.removeEventListener('animationend', cleanup);
            };
            target.addEventListener('animationend', cleanup);
        }
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