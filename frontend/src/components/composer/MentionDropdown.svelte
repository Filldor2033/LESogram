<script lang="ts">
    let {
        users,
        activeIndex,
        onSelect
    }: {
        users: string[];
        activeIndex: number;
        onSelect: (username: string) => void;
    } = $props();
</script>

{#if users.length}
    <div class="mention-dropdown">
        {#each users as username, index}
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
                class="mention-option"
                class:active={
                    index === activeIndex
                }
                onmousedown={(event) => {
                    event.preventDefault();

                    onSelect(username);
                }}
            >
                @{username}
            </div>
        {/each}
    </div>
{/if}