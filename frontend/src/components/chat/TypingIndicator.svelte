<script lang="ts">
    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';
</script>

{#if chatState.typingUsers.length}
    <div
        id="typingIndicator"
        class="typing-indicator"
    >
        {#if chatState.typingUsers.length === 1}
            {t(
                'typingOne',
                {
                    user:
                        chatState.typingUsers[0]
                }
            )}
        {:else}
            {t(
                'typingMany',
                {
                    users:
                        chatState.typingUsers
                            .join(', ')
                }
            )}
        {/if}
    </div>
{/if}