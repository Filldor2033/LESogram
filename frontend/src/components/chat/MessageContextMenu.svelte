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

    let menu = $state<HTMLDivElement>();

    let left = $state(0);
    let top = $state(0);

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

    async function position() {
        if (
            !contextMenuState.open
        ) {
            return;
        }

        await tick();

        const rect =
            menu?.getBoundingClientRect();

        if (!rect) {
            return;
        }

        const padding = 8;

        left = Math.max(
            padding,
            Math.min(
                contextMenuState.x,
                window.innerWidth -
                rect.width -
                padding
            )
        );

        top = Math.max(
            padding,
            Math.min(
                contextMenuState.y,
                window.innerHeight -
                rect.height -
                padding
            )
        );
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
        style={`left:${left}px;top:${top}px`}
        onclick={(event) =>
            event.stopPropagation()}
    >
        <button
            type="button"
            onclick={reply}
        >
            {t('reply')}
        </button>

        {#if canEdit}
            <button
                type="button"
                onclick={edit}
            >
                {t('edit')}
            </button>
        {/if}

        {#if canDelete}
            <button
                type="button"
                class="danger"
                onclick={remove}
            >
                {t('delete')}
            </button>
        {/if}

        <div class="context-reactions">
            {#each reactions as emoji}
                <button
                    type="button"
                    onclick={() =>
                        react(emoji)}
                >
                    {emoji}
                </button>
            {/each}
        </div>
    </div>
{/if}