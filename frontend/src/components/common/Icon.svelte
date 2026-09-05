<script lang="ts">
    import {
        iconPath,
        type IconName
    } from '$lib/icons';

    let {
        name,
        size = 18,
        class: className = ''
    }: {
        name: IconName;
        size?: number;
        class?: string;
    } = $props();

    let d = $derived(iconPath(name));
</script>

<svg
    class={`icon ${className}`}
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
>
    <path {d} />
</svg>
