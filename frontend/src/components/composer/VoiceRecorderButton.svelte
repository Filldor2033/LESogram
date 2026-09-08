<script lang="ts">
    import { onDestroy } from 'svelte';

    import { fly } from 'svelte/transition';

    import Icon from '$components/common/Icon.svelte';

    import {
        VoiceRecorder,
        concatVoiceToWav,
        formatVoiceDuration,
        resampleWave,
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
            durationSec: number,
            waveform?: number[]
        ) => void;
        onError: (message: string) => void;
        disabled?: boolean;
    } = $props();

    let recorder = $state(new VoiceRecorder());

    let recording = $state(false);
    let paused = $state(false);
    let elapsed = $state(0);
    let levels = $state<number[]>([]);
    let level = $state(0);

    /*
     * A recording is split into committed parts and a live segment.
     * When the user trims on pause and then continues recording, the
     * edited segment is committed (immutable) and new audio records
     * as a fresh segment after it. On send everything is merged into
     * one WAV.
     */
    let parts: Blob[] = [];
    let partWaves: number[][] = [];
    let baseDur = $state(0);

    // Trim state for the CURRENT segment (seconds within it).
    let trimFrom = $state(0);
    let trimTo = $state(0);
    let dragging: 'from' | 'to' | null = null;

    // Full-segment waveform shown while paused (the live bars are
    // only a rolling window of the last seconds).
    let segWave = $state<number[]>([]);

    let sending = $state(false);

    // ---- pause-time preview ----
    let previewUrl = $state('');
    let previewAudio: HTMLAudioElement | null = null;
    let previewing = $state(false);
    let previewAt = $state(0);

    const MAX_DURATION = 300; // 5 min
    const MIN_TRIM = 0.3;
    const WAVE_BARS = 56;

    $effect(() => {
        // Re-binds on every new recorder instance (created after each
        // finish()/commit so a bad-state recorder never leaks onward).
        const active = recorder;

        active.onTick = (sec) => {
            elapsed = baseDur + sec;

            if (elapsed >= MAX_DURATION) {
                void pauseOrFinish();
            }
        };

        active.onAmplitude = (peak) => {
            level = peak;

            if (levels.length < WAVE_BARS) {
                levels = [...levels, peak];
            } else {
                levels = [...levels.slice(1), peak];
            }
        };
    });

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

        // Never inherit state from a previous session.
        parts = [];
        partWaves = [];
        baseDur = 0;
        trimFrom = 0;
        trimTo = 0;
        segWave = [];

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
        if (!recording || sending) return;

        if (!paused) {
            recorder.pause();
            paused = true;

            // The trim window covers the current segment.
            trimFrom = 0;
            trimTo = elapsed - baseDur;

            // The editor shows the whole segment, not the rolling window.
            segWave = resampleWave(recorder.amplitude, WAVE_BARS);

            // A stale preview URL must not leak into the new pause.
            teardownPreview();
        } else {
            const seg = elapsed - baseDur;
            const wantsTrim = trimFrom > 0.05 || trimTo < seg - 0.05;

            if (wantsTrim) {
                // Commit the edit and keep recording after it.
                void commitTrimAndContinue();
            } else {
                stopPreview();
                recorder.resume();
                paused = false;
            }
        }
    }

    async function pauseOrFinish() {
        if (paused) {
            await finish();
        } else {
            togglePause();
        }
    }

    /**
     * Applies the trim made on pause and continues recording: the
     * edited segment is frozen into `parts`, and a fresh recorder
     * picks up where the kept audio ends.
     */
    async function commitTrimAndContinue() {
        if (sending) return;
        sending = true;

        // The current recorder's amplitude track — captured before
        // the instance is swapped.
        const recorderPrevWave = recorder.amplitude.slice();

        try {
            const seg = elapsed - baseDur;
            const part = await recorder.stop();

            if (part) {
                const wantsTrim =
                    trimFrom > 0.05 || trimTo < seg - 0.05;

                if (wantsTrim) {
                    let trimmed: Blob | null = null;

                    try {
                        trimmed = await trimVoiceToWav(
                            part.blob,
                            trimFrom,
                            trimTo
                        );
                    } catch {
                        trimmed = null;
                    }

                    if (trimmed) {
                        parts.push(trimmed);

                        partWaves.push(
                            sliceWave(
                                recorderPrevWave,
                                trimFrom / seg,
                                trimTo / seg
                            )
                        );

                        baseDur += trimTo - trimFrom;
                    } else {
                        // Decode failed — keep the segment uncut.
                        console.error(
                            '[voice] trim on continue failed — keeping the segment uncut'
                        );
                        parts.push(part.blob);
                        baseDur += part.durationSec;
                    }
                } else {
                    parts.push(part.blob);
                    baseDur += part.durationSec;
                }
            }

            teardownPreview();

            const next = new VoiceRecorder();
            await next.start();
            recorder = next;

            paused = false;
            trimFrom = 0;
            trimTo = 0;
            segWave = [];
        } catch (err) {
            console.error('[voice] continue after trim failed:', err);
            onError('voiceMicDenied');

            // End the session — the user can start a new one.
            recording = false;
            paused = false;
            parts = [];
            partWaves = [];
            baseDur = 0;
            recorder = new VoiceRecorder();
        } finally {
            sending = false;
        }
    }

    async function finish() {
        if (!recording || sending) return;

        // Sent while recording (not paused): keep the whole current
        // segment — committed parts are already trimmed.
        let from = trimFrom;
        let to = trimTo;

        if (!paused) {
            from = 0;
            to = Number.POSITIVE_INFINITY;
        }

        // Validate BEFORE stopping, so a bad selection doesn't
        // destroy the recording.
        if (to - from < MIN_TRIM) {
            onError('voiceTrimTooShort');
            return;
        }

        stopPreview();

        sending = true;

        try {
            const result = await recorder.stop();
            recording = false;
            paused = false;

            if (!result && parts.length === 0) {
                onError('voiceTooShort');
                return;
            }

            let finalBlob: Blob | null = null;
            let finalDur = 0;

            // Segment trim bounds + wave, used for the final waveform.
            const recorderPrevWaveFinal = recorder.amplitude.slice();
            let segDurFinal = result?.durationSec ?? 0;
            let fromFinal = from;
            let toActualFinal = to;

            if (result) {
                const segDur = result.durationSec;
                const toActual =
                    to === Number.POSITIVE_INFINITY
                        ? segDur
                        : Math.min(to, segDur);

                fromFinal = from;
                toActualFinal = toActual;
                segDurFinal = segDur;

                finalBlob = result.blob;
                finalDur = segDur;

                const wantsTrim =
                    from > 0.05 || toActual < segDur - 0.05;

                if (wantsTrim) {
                    let trimmed: Blob | null = null;

                    try {
                        trimmed = await trimVoiceToWav(
                            result.blob,
                            from,
                            toActual
                        );
                    } catch {
                        trimmed = null;
                    }

                    if (trimmed) {
                        finalBlob = trimmed;
                        finalDur = toActual - from;
                    } else {
                        console.error(
                            '[voice] trim decode failed — sending the segment uncut'
                        );
                    }
                }
            }

            // Full waveform: committed parts + the final segment.
            const fullWave: number[] = [];

            for (const w of partWaves) {
                for (const v of w) fullWave.push(v);
            }

            const segWaveFull = recorderPrevWaveFinal;

            if (segWaveFull) {
                fullWave.push(
                    ...sliceWave(
                        segWaveFull,
                        from / segDurFinal,
                        toActualFinal / segDurFinal
                    )
                );
            }

            const wave =
                fullWave.length > 0
                    ? resampleWave(fullWave, WAVE_BARS)
                    : undefined;

            if (parts.length > 0) {
                const blobs = finalBlob ? [...parts, finalBlob] : parts;

                const merged = await concatVoiceToWav(blobs);

                if (merged) {
                    onSend(
                        merged,
                        Math.round((baseDur + finalDur) * 10) / 10,
                        wave
                    );
                } else {
                    console.error(
                        '[voice] concat failed — sending the last part only'
                    );

                    const last = finalBlob ?? parts[parts.length - 1];
                    onSend(last, Math.round(finalDur * 10) / 10, wave);
                }
            } else {
                onSend(finalBlob!, Math.round(finalDur * 10) / 10, wave);
            }
        } catch (err) {
            console.error('[voice] finish failed:', err);
            onError('voiceSendFailed');
        } finally {
            sending = false;
            resetSession();
        }
    }

    async function cancel() {
        if (!recording || sending) return;

        stopPreview();
        await recorder.cancel();
        recording = false;
        paused = false;
        resetSession();
    }

    function resetSession() {
        parts = [];
        partWaves = [];
        baseDur = 0;
        trimFrom = 0;
        trimTo = 0;
        segWave = [];
        teardownPreview();
        recorder = new VoiceRecorder();
    }

    // ---- trim dragging ----

    // The bars element captured at drag start — event.currentTarget
    // is meaningless inside window-level mousemove handlers.
    let dragBars: HTMLElement | null = null;

    function startDrag(which: 'from' | 'to', e: MouseEvent | TouchEvent) {
        e.stopPropagation();
        dragging = which;
        dragBars = (e.currentTarget as HTMLElement).closest('.voice-rec-bars');

        const clientX = (ev: MouseEvent | TouchEvent): number =>
            ev instanceof MouseEvent
                ? ev.clientX
                : ev.touches[0]?.clientX ?? 0;

        const move = (ev: MouseEvent | TouchEvent) => {
            ev.preventDefault();
            moveDragAt(clientX(ev));
        };

        const up = () => {
            dragging = null;
            dragBars = null;
            window.removeEventListener('mousemove', move as (ev: MouseEvent) => void);
            window.removeEventListener('mouseup', up);
            window.removeEventListener('touchmove', move as (ev: TouchEvent) => void);
            window.removeEventListener('touchend', up);
        };

        window.addEventListener('mousemove', move as (ev: MouseEvent) => void);
        window.addEventListener('mouseup', up);
        window.addEventListener('touchmove', move as (ev: TouchEvent) => void, { passive: false });
        window.addEventListener('touchend', up);
    }

    function moveDragAt(clientX: number) {
        if (!dragBars || !dragging) return;

        const seg = elapsed - baseDur;
        if (seg <= 0) return;

        const rect = dragBars.getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));

        if (dragging === 'from') {
            trimFrom = Math.max(0, Math.min(frac * seg, trimTo - MIN_TRIM));
        } else if (dragging === 'to') {
            trimTo = Math.min(seg, Math.max(frac * seg, trimFrom + MIN_TRIM));
        }
    }

    function resetTrim() {
        trimFrom = 0;
        trimTo = elapsed - baseDur;
    }

    /** Slices a bar array to a fractional [from, to] range. */
    function sliceWave(wave: number[], from: number, to: number): number[] {
        if (wave.length === 0) return [];

        const a = Math.max(0, Math.min(1, from)) * wave.length;
        const b = Math.max(0, Math.min(1, to)) * wave.length;

        const out: number[] = [];

        for (let x = a; x < b; x += wave.length / WAVE_BARS) {
            out.push(wave[Math.floor(x)] ?? 0);
        }

        return out;
    }

    /**
     * Plays the kept part of the current segment so the user can
     * listen to the edit before sending. Playing stops when it
     * reaches the trim end (or the segment end).
     */
    async function togglePreview() {
        if (previewing) {
            previewAudio?.pause();
            return;
        }

        try {
            if (!previewUrl) {
                const seg = await recorder.snapshotForPreview();
                if (!seg) return;
                previewUrl = URL.createObjectURL(seg);
            }

            if (!previewAudio) {
                previewAudio = new Audio(previewUrl);
                previewAudio.addEventListener('ended', () => {
                    previewing = false;
                    previewAt = 0;
                });
                previewAudio.addEventListener('timeupdate', () => {
                    if (!previewAudio) return;
                    previewAt = previewAudio.currentTime;

                    // stop at the trim end
                    if (previewAudio.currentTime >= trimTo) {
                        previewAudio.pause();
                        previewing = false;
                        previewAt = 0;
                    }
                });
            }

            // restart from the trim start each time
            previewAudio.currentTime = Math.min(trimFrom, (previewAudio.duration || Infinity) - 0.05);
            await previewAudio.play();
            previewing = true;
        } catch (err) {
            console.error('[voice] preview failed:', err);
        }
    }

    function stopPreview() {
        if (previewAudio) {
            previewAudio.pause();
        }
        previewing = false;
        previewAt = 0;
    }

    function teardownPreview() {
        stopPreview();
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
        previewUrl = '';
        previewAudio = null;
    }

    const segElapsed = $derived(elapsed - baseDur);
    const previewPct = $derived(
        previewing || previewAt > 0
            ? Math.min(
                  100,
                  Math.max(
                      0,
                      ((trimFrom + previewAt) / Math.max(segElapsed, 0.001)) * 100
                  )
              )
            : 0
    );
    const fromPct = $derived(segElapsed > 0 ? (trimFrom / segElapsed) * 100 : 0);
    const toPct = $derived(segElapsed > 0 ? (trimTo / segElapsed) * 100 : 100);
    const keepDur = $derived(baseDur + (trimTo - trimFrom));

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
                {#if paused}
                    <div
                        class="vbar-mask left"
                        style="width: {fromPct}%"
                    ></div>
                    <div
                        class="vbar-mask right"
                        style="width: {100 - toPct}%"
                    ></div>
                    {#if previewPct > 0}
                        <div
                            class="vbar-progress"
                            style="width: {previewPct}%"
                        ></div>
                    {/if}
                {/if}

                {#if paused && segWave.length > 0}
                    {#each segWave as l, i (i)}
                        <div
                            class="vbar"
                            style="height: {Math.max(14, Math.round((0.14 + l * 0.86) * 100))}%"
                        ></div>
                    {/each}
                {:else}
                    {#each levels as l, i (i)}
                        <div
                            class="vbar"
                            style="height: {Math.max(14, Math.round((0.14 + l * 0.86) * 100))}%"
                        ></div>
                    {:else}
                        <div class="vbar" style="height: 16%"></div>
                    {/each}
                {/if}

                {#if paused}
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div
                        class="trim-handle from"
                        style="left: calc({fromPct}% - 7px)"
                        onmousedown={(e) => startDrag('from', e)}
                        ontouchstart={(e) => startDrag('from', e)}
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
                        ontouchstart={(e) => startDrag('to', e)}
                        role="slider"
                        aria-label="trim end"
                        aria-valuemin={Math.round(trimFrom + MIN_TRIM)}
                        aria-valuemax={Math.round(segElapsed)}
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
                class="voice-rec-btn voice-rec-play"
                type="button"
                title={previewing ? t('pause') : t('play')}
                aria-label={previewing ? t('pause') : t('play')}
                onclick={() => void togglePreview()}
            >
                <Icon name={previewing ? 'pause' : 'play'} size={15} />
            </button>

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
                disabled={trimFrom === 0 && trimTo === segElapsed}
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
