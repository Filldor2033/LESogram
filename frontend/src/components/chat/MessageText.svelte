<script lang="ts">
    import {
        splitMessageText
    } from '$lib/utils/messages';

    let {
        text
    }: {
        text: string;
    } = $props();

    let parts = $derived(
        splitMessageText(text)
    );
</script>

<div class="msg-text">
    {#each parts as part}
        {#if part.mention}
            <span class="mention">
                {part.text}
            </span>
        {:else}
            {part.text}
        {/if}
    {/each}
</div>