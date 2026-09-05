<script lang="ts">
    import {
        tick
    } from 'svelte';

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
        t
    } from '$lib/i18n/i18n.svelte';

    import Icon
        from '$components/common/Icon.svelte';

    let menu = $state<HTMLDivElement>();

    let left = $state(0);
    let top = $state(0);

    let visible = $state(false);

    const reactions = [
        '👍',
        '❤️',
        '😂',
        '😮',
        '😢',
        '🔥'
    ];

    let message = $derived(
        contextMenuState.message
    );

    let canEdit = $derived(
        Boolean(
            message?.id &&
            message.username ===
                authState.username &&
            message.content_type ===
                'text'
        )
    );

    let canDelete = $derived(
        Boolean(
            message?.id &&
            authState.isAdmin
        )
    );

    let isTouch = $derived(
        contextMenuState.touch
    );

    $effect(() => {
        contextMenuState.open;
        contextMenuState.x;
        contextMenuState.y;

        void position();
    });

    async function position() {
        if (
            !contextMenuState.open
        ) {
            return;
        }

        visible = false;

        await tick();

        if (!menu) {
            return;
        }

        /*
         * Ensure the menu is parented to <body> BEFORE
         * measuring: inside the chat panel the coordinates
         * would be panel-relative (backdrop-filter creates
         * a containing block).
         */
        if (menu.parentElement !== document.body) {
            document.body.appendChild(menu);
        }

        /*
         * offsetWidth/Height are layout sizes: unaffected by
         * the scale() transform on the not-yet-visible menu
         * (getBoundingClientRect would measure it shrunk).
         */
        const menuWidth = menu.offsetWidth;
        const menuHeight = menu.offsetHeight;

        const padding = 8;

        left = Math.min(
            Math.max(
                padding,
                contextMenuState.x
            ),
            window.innerWidth -
                menuWidth -
                padding
        );

        /*
         * On touch devices the menu opens at the finger
         * point: shift it up so the finger does not cover
         * it.
         */
        const cursorShift =
            isTouch ? 12 : 10;

        top = Math.min(
            Math.max(
                padding,
                contextMenuState.y -
                    cursorShift
            ),
            window.innerHeight -
                menuHeight -
                padding
        );

        await tick();

        requestAnimationFrame(() => {
            visible = true;
        });
    }

    $effect(() => {
        contextMenuState.open;
        contextMenuState.x;
        contextMenuState.y;

        void position();
    });

    function close() {
        contextMenuState.close();
    }

    function reply() {
        if (message) {
            messageActions.reply(
                message
            );
        }

        close();
    }

    function edit() {
        if (message) {
            messageActions.startEdit(
                message
            );
        }

        close();
    }

    function remove() {
        if (message) {
            void messageActions.delete(
                message
            );
        }

        close();
    }

    function react(
        emoji: string
    ) {
        if (message) {
            void messageActions.react(
                message,
                emoji
            );
        }

        close();
    }
</script>

<svelte:window
    onclick={close}
    onresize={close}
    onkeydown={(event) => {
        if (event.key === 'Escape') {
            close();
        }
    }}
/>

{#if message}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
        bind:this={menu}
        class="context-menu"
        class:visible
        style={`left:${left}px;top:${top}px`}
        onclick={(event) =>
            event.stopPropagation()}
        role="menu"
        tabindex="-1"
    >
        <div class="context-reactions">
            {#each reactions as emoji, i}
                <button
                    type="button"
                    class="reaction-btn"
                    style={`transition-delay:${i * 24}ms`}
                    onclick={() =>
                        react(emoji)}
                >
                    {emoji}
                </button>
            {/each}
        </div>

        <div class="context-sep"></div>

        <button
            type="button"
            class="context-action"
            onclick={reply}
        >
            <Icon name="reply" />

            <span>{t('reply')}</span>
        </button>

        {#if canEdit}
            <button
                type="button"
                class="context-action"
                onclick={edit}
            >
                <Icon name="edit" />

                <span>{t('edit')}</span>
            </button>
        {/if}

        {#if canDelete}
            <button
                type="button"
                class="context-action danger"
                onclick={remove}
            >
                <Icon name="trash" />

                <span>{t('delete')}</span>
            </button>
        {/if}
    </div>
{/if}
