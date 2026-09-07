<script lang="ts">
    import { onDestroy } from 'svelte';

    import { fly } from 'svelte/transition';

    import Icon from '$components/common/Icon.svelte';

    import {
        VoiceRecorder,
        formatVoiceDuration
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
    let elapsed = $state(0);
    let levels = $state<number[]>([]);

    const MAX_DURATION = 300; // 5 min

    $effect(() => {
        recorder.onTick = (sec) => {
            elapsed = sec;

            if (sec >= MAX_DURATION) {
                void finish();
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
            onError('voiceNotSupported');
            return;
        }

        try {
            await recorder.start();
            recording = true;
            elapsed = 0;
            levels = [];
        } catch {
            onError('voiceMicDenied');
        }
    }

    async function finish() {
        if (!recording) return;

        const result = await recorder.stop();
        recording = false;

        if (!result) {
            onError('voiceTooShort');
            return;
        }

        onSend(result.blob, result.durationSec);
    }

    async function cancel() {
        if (!recording) return;

        await recorder.cancel();
        recording = false;
    }

    onDestroy(() => {
        void recorder.cancel();
    });
</script>

{#if recording}
    <div
        class="voice-rec"
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
            <span class="voice-rec-dot"></span>

            <div class="voice-rec-bars">
                {#each levels as l, i (i)}
                    <div
                        class="vbar"
                        style="height: {Math.max(14, Math.round((0.14 + l * 0.86) * 100))}%"
                    ></div>
                {:else}
                    <div class="vbar" style="height: 16%"></div>
                {/each}
            </div>

            <span class="voice-rec-timer">
                {formatVoiceDuration(elapsed)}
            </span>
        </div>

        <button
            class="voice-rec-btn voice-rec-send"
            type="button"
            title={t('voiceSendAction')}
            aria-label={t('voiceSendAction')}
            onclick={finish}
        >
            <Icon name="send" size={15} />
        </button>
    </div>
{:else}
    <button
        class="secondary tool-btn voice-btn"
        style="max-width:40px"
        type="button"
        disabled={disabled}
        title={t('voiceRecord')}
        aria-label={t('voiceRecord')}
        onclick={start}
    >
        <Icon name="mic" size={17} />
    </button>
{/if}
