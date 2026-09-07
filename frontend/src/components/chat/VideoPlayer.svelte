<script lang="ts">
    import Icon from '$components/common/Icon.svelte';
    import { t } from '$lib/i18n/i18n.svelte';

    let {
        src,
        file_name
    }: {
        src: string;
        file_name?: string;
    } = $props();

    let video = $state<HTMLVideoElement>();
    let root = $state<HTMLDivElement>();

    let playing = $state(false);
    let current = $state(0);
    let duration = $state(0);
    let volume = $state(1);
    let muted = $state(false);
    let rate = $state(1);
    let showControls = $state(true);
    let buffered = $state(0);
    let hoverTime = $state<number | null>(null);
    let scrubbing = $state(false);
    let hideTimer: ReturnType<typeof setTimeout> | null = null;

    const RATES = [1, 1.25, 1.5, 2];

    function fmt(s: number): string {
        if (!Number.isFinite(s)) return '0:00';
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60);
        return `${m}:${sec.toString().padStart(2, '0')}`;
    }

    function wake() {
        showControls = true;
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {
            if (playing && !scrubbing) showControls = false;
        }, 2200);
    }

    export function toggle() {
        if (!video) return;
        if (video.paused) {
            void video.play();
        } else {
            video.pause();
        }
    }

    function onPlay() {
        playing = true;
        wake();
    }

    function onPause() {
        playing = false;
        showControls = true;
        if (hideTimer) clearTimeout(hideTimer);
    }

    function onTime() {
        if (video) current = video.currentTime;
    }

    function onLoaded() {
        if (video) duration = video.duration || 0;
    }

    function onProgress() {
        if (!video || !video.buffered.length) return;
        buffered = video.buffered.end(video.buffered.length - 1);
    }

    function seekTo(e: MouseEvent) {
        const bar = e.currentTarget as HTMLElement;
        const rect = bar.getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
        if (video && duration) video.currentTime = frac * duration;
    }

    function startScrub(e: MouseEvent) {
        scrubbing = true;
        seekTo(e);
        const move = (ev: MouseEvent) => seekTo(ev);
        const up = () => {
            scrubbing = false;
            window.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', up);
            wake();
        };
        window.addEventListener('mousemove', move);
        window.addEventListener('mouseup', up);
    }

    function hoverTimeAt(e: MouseEvent): number | null {
        const bar = e.currentTarget as HTMLElement;
        const rect = bar.getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
        return duration ? frac * duration : null;
    }

    function setVolume(v: number) {
        volume = v;
        if (video) {
            video.volume = v;
            video.muted = v === 0;
        }
        muted = v === 0;
    }

    function toggleMute() {
        if (!video) return;
        muted = !muted;
        video.muted = muted;
    }

    function cycleRate() {
        const i = RATES.indexOf(rate);
        rate = RATES[(i + 1) % RATES.length];
        if (video) video.playbackRate = rate;
    }

    function skip(delta: number) {
        if (video) video.currentTime = Math.max(0, Math.min(duration, video.currentTime + delta));
        wake();
    }

    function fullscreen() {
        if (!root) return;
        if (document.fullscreenElement) {
            void document.exitFullscreen();
        } else {
            void root.requestFullscreen();
        }
    }

    $effect(() => {
        return () => {
            if (hideTimer) clearTimeout(hideTimer);
        };
    });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_mouse_events_have_key_events -->
<div
    class="vp"
    bind:this={root}
    onmousemove={wake}
    onmouseleave={() => {
        if (playing && !scrubbing) showControls = false;
    }}
>
    <!-- svelte-ignore a11y_media_has_caption -->
    <video
        bind:this={video}
        {src}
        preload="metadata"
        playsinline
        onclick={toggle}
        onplay={onPlay}
        onpause={onPause}
        ontimeupdate={onTime}
        onloadedmetadata={onLoaded}
        onprogress={onProgress}
    ></video>

    {#if !playing && current === 0}
        <button
            class="vp-bigplay"
            type="button"
            aria-label={t('play')}
            onclick={toggle}
        >
            <Icon name="play" size={26} />
        </button>
    {/if}

    <div
        class="vp-controls"
        class:visible={showControls || !playing}
    >
        <div
            class="vp-progress"
            role="slider"
            aria-label={t('seek')}
            aria-valuemin={0}
            aria-valuemax={Math.round(duration)}
            aria-valuenow={Math.round(current)}
            tabindex="0"
            onmousedown={startScrub}
            onmousemove={(e) => (hoverTime = hoverTimeAt(e))}
            onmouseleave={() => (hoverTime = null)}
        >
            <div
                class="vp-buffer"
                style="width: {duration ? (buffered / duration) * 100 : 0}%"
            ></div>
            <div
                class="vp-fill"
                style="width: {duration ? (current / duration) * 100 : 0}%"
            >
                <div class="vp-knob"></div>
            </div>

            {#if hoverTime !== null && duration}
                <div
                    class="vp-hover"
                    style="left: {(hoverTime / duration) * 100}%"
                >
                    {fmt(hoverTime)}
                </div>
            {/if}
        </div>

        <div class="vp-row">
            <button
                class="vp-btn"
                type="button"
                aria-label={playing ? t('pause') : t('play')}
                onclick={toggle}
            >
                <Icon name={playing ? 'pause' : 'play'} size={17} />
            </button>

            <button
                class="vp-btn vp-skip"
                type="button"
                aria-label="-10s"
                onclick={() => skip(-10)}
            >
                <span class="vp-skip-num">10</span>
                <Icon name="skip-back" size={15} />
            </button>

            <button
                class="vp-btn vp-skip"
                type="button"
                aria-label="+10s"
                onclick={() => skip(10)}
            >
                <Icon name="skip-forward" size={15} />
                <span class="vp-skip-num">10</span>
            </button>

            <div class="vp-time">
                {fmt(current)} / {fmt(duration)}
            </div>

            <div class="vp-spacer"></div>

            <div class="vp-volume">
                <button
                    class="vp-btn"
                    type="button"
                    aria-label={t('volume')}
                    onclick={toggleMute}
                >
                    <Icon name={muted || volume === 0 ? 'volume-off' : 'volume'} size={17} />
                </button>
                <input
                    class="vp-vol"
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={muted ? 0 : volume}
                    aria-label={t('volume')}
                    oninput={(e) => setVolume(parseFloat((e.target as HTMLInputElement).value))}
                />
            </div>

            <button
                class="vp-btn vp-rate"
                type="button"
                aria-label={t('speed')}
                onclick={cycleRate}
            >
                {rate}×
            </button>

            <button
                class="vp-btn"
                type="button"
                aria-label={t('fullscreen')}
                onclick={fullscreen}
            >
                <Icon name="expand" size={16} />
            </button>
        </div>
    </div>
</div>
