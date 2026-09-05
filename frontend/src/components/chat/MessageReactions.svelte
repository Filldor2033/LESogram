<script lang="ts">
    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        messageActions
    } from '$lib/services/message-actions.svelte';

    import type {
        Message
    } from '$lib/types/message';

    let {
        message
    }: {
        message: Message;
    } = $props();

    let entries = $derived(
        Object.entries(
            message.reactions ?? {}
        )
    );
</script>

{#if entries.length}
    <div class="msg-reactions">
        {#each entries as [emoji, users]}
            <button
                type="button"
                class="msg-reaction"
                class:active={
                    users.includes(
                        authState.username
                    )
                }
                title={users.join(', ')}
                onclick={(event) => {
                    event.stopPropagation();

                    void messageActions
                        .react(
                            message,
                            emoji
                        );
                }}
            >
                {emoji} {users.length}
            </button>
        {/each}
    </div>
{/if}