<script lang="ts">
    import Icon from '$components/common/Icon.svelte';
    import { t } from '$lib/i18n/i18n.svelte';
    import { formatVoiceDuration } from '$lib/utils/voice-recorder';

    let {
        src,
        durationSec,
        waveform,
        own = false
    }: {
        src: string;
        durationSec?: number | null;
        waveform?: string | null;
        own?: boolean;
    } = $props();

    let audio = $state<HTMLAudioElement>();
    let playing = $state(false);
    let current = $state(0);
    let fallbackDuration = $state(0);
    let error = $state(false);

    let duration = $derived(
        Number.isFinite(audio?.duration ?? NaN)
            ? audio!.duration
            : fallbackDuration
    );

    // follow the prop until real metadata arrives
    $effect(() => {
        fallbackDuration = durationSec ?? 0;
    });

    /*
     * Real waveform recorded on the client (JSON array of 0..1
     * amplitudes). Falls back to a stable pseudo-waveform derived
     * from the message id when absent (old messages).
     */
    let realBars = $derived.by(() => {
        if (!waveform) return null;

        try {
            const arr = JSON.parse(waveform);

            if (
                !Array.isArray(arr) ||
                arr.length === 0 ||
                !arr.every((v) => typeof v === 'number' && Number.isFinite(v))
            ) {
                return null;
            }

            return arr.slice(0, 64).map((v: number) => Math.max(0.14, Math.min(1, v)));
        } catch {
            return null;
        }
    });

    // Synthetic pseudo-waveform derived from the message id —
    // stable per message, looks organic
    let bars = $derived.by(() => {
        if (realBars) return realBars;

        const seedInput = src.slice(-24);
        let hash = 2166136261;

        for (let i = 0; i < seedInput.length; i++) {
            hash ^= seedInput.charCodeAt(i);
            hash = Math.imul(hash, 16777619);
        }

        const out: number[] = [];
        let x = (hash >>> 0) / 4294967296;

        for (let i = 0; i < 32; i++) {
            x = (x * 9301 + 49297) % 233280;
            const base = 0.25 + (x / 233280) * 0.55;
            // taper the ends slightly
            const edge = Math.min(i, 31 - i) < 3 ? 0.65 : 1;
            out.push(Math.min(1, base * edge));
        }

        return out;
    });

    let progress = $derived(
        duration > 0 ? Math.min(1, current / duration) : 0
    );

    function toggle() {
        if (!audio) return;

        if (audio.paused) {
            audio.currentTime = 0;
            void audio.play();
        } else {
            audio.pause();
        }
    }

    function onLoaded() {
        if (audio && Number.isFinite(audio.duration)) {
            fallbackDuration = audio.duration;
        }
    }

    function onEnded() {
        playing = false;
        current = 0;
    }

    function seek(e: MouseEvent) {
        if (!audio || !duration) return;
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
        audio.currentTime = frac * duration;
        current = audio.currentTime;

        if (audio.paused) {
            void audio.play();
        }
    }
</script>

<div class="voice" class:own>
    <button
        class="voice-play"
        type="button"
        aria-label={playing ? t('pause') : t('play')}
        onclick={toggle}
    >
        <Icon name={playing ? 'pause' : 'play'} size={13} />
    </button>

    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
        class="voice-wave"
        class:real-wave={realBars !== null}
        role="slider"
        aria-label={t('seek')}
        aria-valuemin={0}
        aria-valuemax={Math.round(duration)}
        aria-valuenow={Math.round(current)}
        tabindex="0"
        onclick={seek}
    >
        {#each bars as h, i (i)}
            <div
                class="voice-bar"
                class:played={i / bars.length <= progress}
                style="height: {Math.max(14, Math.round(h * 100))}%"
            ></div>
        {/each}
    </div>

    <div class="voice-time">
        {formatVoiceDuration(playing || current > 0 ? duration - current : duration)}
    </div>

    {#if error}
        <span class="voice-error">⚠</span>
    {/if}

    <!-- svelte-ignore a11y_media_has_caption -->
    <audio
        bind:this={audio}
        {src}
        preload="metadata"
        onplay={() => (playing = true)}
        onpause={() => (playing = false)}
        ontimeupdate={() => audio && (current = audio.currentTime)}
        onloadedmetadata={onLoaded}
        onended={onEnded}
        onerror={() => (error = true)}
    ></audio>
</div>
