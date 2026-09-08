<script lang="ts">
    import { onDestroy } from 'svelte';

    import { fly } from 'svelte/transition';

    import Icon from '$components/common/Icon.svelte';

    import {
        VoiceRecorder,
        formatVoiceDuration,
        trimVoiceToWav
    } from '$lib/utils/voice-recorder';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    let {
        onSend,
        onError,
        disabled = false
    }: {
        onSend: (
            blob: Blob,
            durationSec: number
        ) => void;
        onError: (message: string) => void;
        disabled?: boolean;
    } = $props();

    let recorder = new VoiceRecorder();

    let recording = $state(false);
    let paused = $state(false);
    let elapsed = $state(0);
    let levels = $state<number[]>([]);

    // trim state (on pause)
    let trimFrom = $state(0);
    let trimTo = $state(0);
    let dragging: 'from' | 'to' | null = null;

    let sending = $state(false);

    const MAX_DURATION = 300; // 5 min
    const MIN_TRIM = 0.3;

    $effect(() => {
        recorder.onTick = (sec) => {
            elapsed = sec;

            if (sec >= MAX_DURATION) {
                void pauseOrFinish();
            }
        };

        recorder.onAmplitude = (peak) => {
            level = peak;

            if (levels.length < 56) {
                levels = [...levels, peak];
            } else {
                levels = [...levels.slice(1), peak];
            }
        };
    });

    let level = $state(0);

    async function start() {
        if (recording || disabled) return;

        if (!VoiceRecorder.supported) {
            onError(
                VoiceRecorder.insecureContext
                    ? 'voiceInsecure'
                    : 'voiceNotSupported'
            );
            return;
        }

        try {
            const perm = await navigator.permissions.query({
                name: 'microphone' as PermissionName
            });

            console.info('[voice] mic permission state:', perm.state);

            if (perm.state === 'denied') {
                console.error(
                    '[voice] denied at permissions.query — this is either a site-level block,' +
                    ' the global Chrome setting (chrome://settings/content/microphone),' +
                    ' or an OS-level privacy block (Windows/macOS).'
                );
                onError('voiceMicBlocked');
                return;
            }
        } catch (e) {
            console.info('[voice] permissions.query unavailable:', e);
        }

        try {
            await recorder.start();
            recording = true;
            paused = false;
            elapsed = 0;
            levels = [];
        } catch (err) {
            console.error('[voice] getUserMedia failed:', err);

            if (err instanceof DOMException) {
                switch (err.name) {
                    case 'NotAllowedError':
                    case 'SecurityError':
                        onError('voiceMicBlocked');
                        break;
                    case 'NotFoundError':
                        onError('voiceNoDevice');
                        break;
                    case 'NotReadableError':
                    case 'OverconstrainedError':
                        onError('voiceMicBusy');
                        break;
                    default:
                        onError('voiceMicDenied');
                }
            } else {
                onError('voiceMicDenied');
            }
        }
    }

    /** Pause: freeze the recording and open the trim editor. */
    function togglePause() {
        if (!recording) return;

        if (!paused) {
            recorder.pause();
            paused = true;

            trimFrom = 0;
            trimTo = elapsed;
        } else {
            // resume only if the trim handles are at the ends;
            // otherwise the user is mid-edit — send button applies the trim
            recorder.resume();
            paused = false;
        }
    }

    async function pauseOrFinish() {
        if (paused) {
            await finish();
        } else {
            togglePause();
        }
    }

    async function finish() {
        if (!recording || sending) return;

        // Validate the trim range BEFORE stopping the recorder,
        // so an invalid selection doesn't destroy the recording.
        if (paused && trimTo - trimFrom < MIN_TRIM) {
            onError('voiceTrimTooShort');
            return;
        }

        sending = true;

        try {
            const result = await recorder.stop();
            recording = false;
            paused = false;

            if (!result) {
                onError('voiceTooShort');
                return;
            }

            // Apply trim if the handles moved
            const wantsTrim =
                trimFrom > 0.05 || trimTo < result.durationSec - 0.05;

            if (wantsTrim) {
                const trimmed = await trimVoiceToWav(
                    result.blob,
                    trimFrom,
                    trimTo
                );

                if (trimmed) {
                    onSend(
                        trimmed,
                        Math.round((trimTo - trimFrom) * 10) / 10
                    );
                } else {
                    // trim failed to decode — send original
                    onSend(result.blob, result.durationSec);
                }
            } else {
                onSend(result.blob, result.durationSec);
            }
        } catch (err) {
            console.error('[voice] finish failed:', err);
            onError('voiceSendFailed');
        } finally {
            sending = false;
            trimFrom = 0;
            trimTo = 0;
        }
    }

    async function cancel() {
        if (!recording) return;

        await recorder.cancel();
        recording = false;
        paused = false;
    }

    // ---- trim dragging ----

    // The bars element captured at drag start — event.currentTarget
    // is meaningless inside window-level mousemove handlers.
    let dragBars: HTMLElement | null = null;

    function startDrag(which: 'from' | 'to', e: MouseEvent) {
        e.stopPropagation();
        dragging = which;
        dragBars = (e.currentTarget as HTMLElement).closest('.voice-rec-bars');

        const move = (ev: MouseEvent) => moveDrag(ev);

        const up = () => {
            dragging = null;
            dragBars = null;
            window.removeEventListener('mousemove', move);
            window.removeEventListener('mouseup', up);
        };

        window.addEventListener('mousemove', move);
        window.addEventListener('mouseup', up);
    }

    function moveDrag(e: MouseEvent) {
        if (!dragBars || !dragging) return;

        const rect = dragBars.getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));

        if (dragging === 'from') {
            trimFrom = Math.max(0, Math.min(frac * elapsed, trimTo - MIN_TRIM));
        } else if (dragging === 'to') {
            trimTo = Math.min(elapsed, Math.max(frac * elapsed, trimFrom + MIN_TRIM));
        }
    }

    function resetTrim() {
        trimFrom = 0;
        trimTo = elapsed;
    }

    const fromPct = $derived(elapsed > 0 ? (trimFrom / elapsed) * 100 : 0);
    const toPct = $derived(elapsed > 0 ? (trimTo / elapsed) * 100 : 100);
    const keepDur = $derived(trimTo - trimFrom);

    onDestroy(() => {
        void recorder.cancel();
    });
</script>

{#if recording}
    <div
        class="voice-rec"
        class:paused
        in:fly={{ y: 10, duration: 180 }}
    >
        <button
            class="voice-rec-btn voice-rec-cancel"
            type="button"
            title={t('voiceCancel')}
            aria-label={t('voiceCancel')}
            onclick={cancel}
        >
            <Icon name="close" size={16} />
        </button>

        <div class="voice-rec-visual">
            <span class="voice-rec-dot" class:hidden={paused}></span>

            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="voice-rec-bars" class:editable={paused}>
                <div
                    class="vbar-mask left"
                    style="width: {fromPct}%"
                ></div>
                <div
                    class="vbar-mask right"
                    style="width: {100 - toPct}%"
                ></div>

                {#each levels as l, i (i)}
                    <div
                        class="vbar"
                        style="height: {Math.max(14, Math.round((0.14 + l * 0.86) * 100))}%"
                    ></div>
                {:else}
                    <div class="vbar" style="height: 16%"></div>
                {/each}

                {#if paused}
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div
                        class="trim-handle from"
                        style="left: calc({fromPct}% - 7px)"
                        onmousedown={(e) => startDrag('from', e)}
                        role="slider"
                        aria-label="trim start"
                        aria-valuemin={0}
                        aria-valuemax={Math.round(trimTo - MIN_TRIM)}
                        aria-valuenow={Math.round(trimFrom)}
                        tabindex="0"
                    ></div>
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div
                        class="trim-handle to"
                        style="left: calc({toPct}% - 7px)"
                        onmousedown={(e) => startDrag('to', e)}
                        role="slider"
                        aria-label="trim end"
                        aria-valuemin={Math.round(trimFrom + MIN_TRIM)}
                        aria-valuemax={Math.round(elapsed)}
                        aria-valuenow={Math.round(trimTo)}
                        tabindex="0"
                    ></div>
                {/if}
            </div>

            <span class="voice-rec-timer">
                {formatVoiceDuration(paused ? keepDur : elapsed)}
            </span>
        </div>

        {#if paused}
            <button
                class="voice-rec-btn voice-rec-continue"
                type="button"
                title={t('voiceResume')}
                aria-label={t('voiceResume')}
                onclick={togglePause}
            >
                <Icon name="mic" size={15} />
            </button>

            <button
                class="voice-rec-btn voice-rec-reset"
                type="button"
                title={t('voiceTrimReset')}
                aria-label={t('voiceTrimReset')}
                onclick={resetTrim}
                disabled={trimFrom === 0 && trimTo === elapsed}
            >
                <Icon name="refresh" size={15} />
            </button>
        {:else}
            <button
                class="voice-rec-btn voice-rec-pause"
                type="button"
                title={t('voicePause')}
                aria-label={t('voicePause')}
                onclick={togglePause}
            >
                <Icon name="pause" size={15} />
            </button>
        {/if}

        <button
            class="voice-rec-btn voice-rec-send"
            type="button"
            title={t('voiceSendAction')}
            aria-label={t('voiceSendAction')}
            onclick={() => void finish()}
            disabled={sending}
        >
            <Icon name="send" size={15} />
        </button>
    </div>
{:else}
    <button
        class="secondary tool-btn voice-btn"
        type="button"
        disabled={disabled}
        title={t('voiceRecord')}
        aria-label={t('voiceRecord')}
        onclick={start}
    >
        <Icon name="mic" size={17} />
    </button>
{/if}
