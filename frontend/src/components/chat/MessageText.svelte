<script lang="ts">
    import {
        splitMessageText
    } from '$lib/utils/messages';

    import {
        profileState
    } from '$lib/state/profile.svelte';

    let {
        text
    }: {
        text: string;
    } = $props();

    let parts = $derived(
        splitMessageText(text)
    );

    function openProfile(
        username: string | undefined
    ) {
        if (username) {
            profileState.viewing = username;
        }
    }
</script>

<div class="msg-text">
    {#each parts as part}
        {#if part.mention}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
            <button
                type="button"
                class="mention mention-link"
                onclick={() =>
                    openProfile(part.mentionUser)}
                title={part.mentionUser}
            >
                {part.text}
            </button>
        {:else}
            {part.text}
        {/if}
    {/each}
</div>
