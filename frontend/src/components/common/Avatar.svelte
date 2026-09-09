<script lang="ts">
    import { profileState } from '$lib/state/profile.svelte';

    let {
        username,
        displayName = null,
        url = null,
        size = 28,
        clickToProfile = false
    }: {
        username: string;
        displayName?: string | null | undefined;
        url?: string | null | undefined;
        size?: number;
        clickToProfile?: boolean;
    } = $props();

    // Stable pseudo-color from the username hash (no avatar uploaded)
    const hue = $derived.by(() => {
        let h = 0;

        for (let i = 0; i < username.length; i++) {
            h = (h * 31 + username.charCodeAt(i)) % 360;
        }

        return h;
    });

    const initial = $derived.by(() => {
        const source = displayName?.trim() || username;
        return source.slice(0, 1).toUpperCase();
    });

    function openProfile() {
        if (clickToProfile) {
            profileState.viewing = username;
        }
    }

    function onKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') openProfile();
    }
</script>

{#if url}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
    <img
        class="avatar-img{clickToProfile ? ' clickable' : ''}"
        src={url}
        alt={username}
        style="width: {size}px; height: {size}px"
        loading="lazy"
        onclick={openProfile}
        onkeydown={onKeydown}
        role={clickToProfile ? 'button' : undefined}
        tabindex={clickToProfile ? 0 : undefined}
    />
{:else}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
    <div
        class="avatar-fallback{clickToProfile ? ' clickable' : ''}"
        style="width: {size}px; height: {size}px; font-size: {Math.round(
            size * 0.42
        )}px; background: hsl({hue}, 45%, 38%)"
        onclick={openProfile}
        onkeydown={onKeydown}
        role={clickToProfile ? 'button' : undefined}
        tabindex={clickToProfile ? 0 : undefined}
        title={username}
    >
        {initial}
    </div>
{/if}
