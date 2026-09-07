<script lang="ts">
    import Icon from '$components/common/Icon.svelte';
    import { t } from '$lib/i18n/i18n.svelte';

    let {
        images,
        index,
        onclose
    }: {
        images: { url: string; name?: string }[];
        index: number;
        onclose: () => void;
    } = $props();

    let current = $state(0);
    let scale = $state(1);
    let tx = $state(0);
    let ty = $state(0);
    let panning = $state(false);
    let panStart = $state({ x: 0, y: 0, tx: 0, ty: 0 });

    // follow the `index` prop when it changes from outside
    $effect(() => {
        current = index;
    });

    const total = $derived(images.length);
    const img = $derived(images[current]);

    $effect(() => {
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onclose();
            else if (e.key === 'ArrowRight') next();
            else if (e.key === 'ArrowLeft') prev();
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    });

    function reset() {
        scale = 1;
        tx = 0;
        ty = 0;
    }

    function next() {
        if (!total) return;
        current = (current + 1) % total;
        reset();
    }

    function prev() {
        if (!total) return;
        current = (current - 1 + total) % total;
        reset();
    }

    function zoomIn() {
        scale = Math.min(5, scale * 1.4);
    }

    function zoomOut() {
        scale = Math.max(1, scale / 1.4);
        if (scale === 1) reset();
    }

    function onWheel(e: WheelEvent) {
        e.preventDefault();
        if (e.deltaY < 0) {
            scale = Math.min(5, scale * 1.15);
        } else {
            scale = Math.max(1, scale / 1.15);
            if (scale === 1) reset();
        }
    }

    function startPan(e: MouseEvent) {
        if (scale === 1) return;
        panning = true;
        panStart = { x: e.clientX, y: e.clientY, tx, ty };
        const move = (ev: MouseEvent) => {
            if (!panning) return;
            tx = panStart.tx + (ev.clientX - panStart.x);
            ty = panStart.ty + (ev.clientY - panStart.y);
        };
        const up = () => {
            panning = false;
            window.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', up);
        };
        window.addEventListener('mousemove', move);
        window.addEventListener('mouseup', up);
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
    class="lb"
    onclick={(e) => {
        if (e.target === e.currentTarget) onclose();
    }}
>
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <img
        class="lb-img"
        class:pannable={scale > 1}
        class:panning
        src={img?.url}
        alt={img?.name || 'image'}
        style="transform: translate({tx}px, {ty}px) scale({scale})"
        draggable="false"
        onclick={(e) => {
            e.stopPropagation();
            if (scale === 1) {
                scale = 2;
            } else {
                reset();
            }
        }}
        onmousedown={startPan}
        onwheel={onWheel}
    />

    <div class="lb-top">
        <div class="lb-counter">
            {current + 1} / {total}
        </div>

        <div class="lb-actions">
            <button class="lb-btn" type="button" aria-label={t('zoomOut')} onclick={zoomOut}>
                <Icon name="zoom-out" size={18} />
            </button>
            <button class="lb-btn" type="button" aria-label={t('zoomIn')} onclick={zoomIn}>
                <Icon name="zoom-in" size={18} />
            </button>
            {#if img?.name}
                <a
                    class="lb-btn"
                    href={img.url}
                    download={img.name}
                    aria-label={t('download')}
                >
                    <Icon name="download" size={18} />
                </a>
            {/if}
            <button class="lb-btn" type="button" aria-label={t('close')} onclick={onclose}>
                <Icon name="close" size={18} />
            </button>
        </div>
    </div>

    {#if total > 1}
        <button class="lb-nav lb-prev" type="button" aria-label={t('prev')} onclick={prev}>
            <Icon name="chevron-left" size={26} />
        </button>
        <button class="lb-nav lb-next" type="button" aria-label={t('next')} onclick={next}>
            <Icon name="chevron-right" size={26} />
        </button>
    {/if}
</div>
