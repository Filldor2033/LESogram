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

    let root: HTMLDivElement;

    let replied = $derived(
        chatState.getMessage(
            replyToId
        )
    );

    /*
     * Telegram-style quote sizing: the quote (and thus the
     * replying bubble) is as wide as the quoted message's
     * bubble. Measured live via ResizeObserver so it follows
     * window resizes; falls back to fit-content when the
     * quoted message is not rendered in the current page.
     */
    $effect(() => {
        void chatState.messages
            .length;
        if (!root) {
            return;
        }

        const target =
            document.querySelector<
                HTMLElement
            >(
                `.msg[data-message-id="${replyToId}"]`
            );

        if (!target) {
            root.style.removeProperty(
                '--reply-w'
            );
            return;
        }

        /*
         * Match the VISIBLE bubble widths: the replying
         * bubble renders the quote plus its own horizontal
         * padding (13px/14px → 28px total), so the quote
         * must be 28px narrower than the quoted bubble for
         * both bubbles to end up exactly equal, like
         * Telegram.
         *
         * The quoted bubble plays the msgIn entry animation
         * (scale 0.98 → 1) and is fit-content, so a single
         * early measure lands on a stale/shrunk width. The
         * rAF double-frame re-measure below lets the layout
         * settle; the ResizeObserver keeps it in sync on
         * real changes (window resize, page load) while the
         * equality guard ignores animation jitter.
         */
        let last = -1;

        const apply = () => {
            const width = Math.max(
                80,
                Math.round(
                    target
                        .getBoundingClientRect()
                        .width - 28
                )
            );

            if (width === last) {
                return;
            }

            last = width;
            root.style.setProperty(
                '--reply-w',
                `${width}px`
            );
        };

        requestAnimationFrame(() => {
            requestAnimationFrame(
                apply
            );
        });

        const observer =
            new ResizeObserver(
                apply
            );
        observer.observe(target);

        return () => {
            observer.disconnect();
        };
    });

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
    bind:this={root}
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