<script lang="ts">
    import Avatar from '$components/common/Avatar.svelte';

    import { roomUsersState } from '$lib/state/room-users.svelte';

    let {
        users,
        activeIndex,
        onSelect
    }: {
        users: string[];
        activeIndex: number;
        onSelect: (username: string) => void;
    } = $props();

    /** username -> user object (for the avatar / online dot) */
    let userMap = $derived(
        new Map(
            roomUsersState.users.map(u => [
                u.username,
                u
            ])
        )
    );
</script>

{#if users.length}
    <div class="mention-dropdown">
        {#each users as username, index}
            {@const user = userMap.get(username)}
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div
                class="mention-option"
                class:active={index === activeIndex}
                onmousedown={(event) => {
                    event.preventDefault();
                    onSelect(username);
                }}
            >
                <Avatar
                    {username}
                    displayName={user?.display_name}
                    url={user?.avatar_url}
                    size={22}
                />

                <span class="mention-option-name">
                    {user?.display_name || username}
                </span>

                <span class="mention-option-sub">
                    @{username}
                </span>

                {#if user?.online}
                    <span class="mention-online-dot"></span>
                {/if}
            </div>
        {/each}
    </div>
{/if}
