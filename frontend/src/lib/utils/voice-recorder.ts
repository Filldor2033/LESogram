/**
 * Voice recorder built on MediaRecorder with live
 * amplitude sampling for the waveform preview.
 */

export interface VoiceRecording {
    blob: Blob;
    durationSec: number;
    waveform: number[];
}

const TARGET_SAMPLES = 48;

export class VoiceRecorder {
    private stream: MediaStream | null = null;
    private recorder: MediaRecorder | null = null;
    private chunks: Blob[] = [];
    private ctx: AudioContext | null = null;
    private analyser: AnalyserNode | null = null;
    private rafId: number | null = null;
    private startedAt = 0;
    private stopped = false;

    /** Peak amplitudes sampled while recording. */
    amplitude: number[] = [];
    onAmplitude: ((peak: number) => void) | null = null;
    onTick: ((elapsed: number) => void) | null = null;

    static get supported(): boolean {
        return (
            typeof navigator !== 'undefined' &&
            !!navigator.mediaDevices?.getUserMedia &&
            typeof MediaRecorder !== 'undefined'
        );
    }

    static pickMimeType(): string {
        const candidates = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/ogg'
        ];

        for (const type of candidates) {
            if (MediaRecorder.isTypeSupported?.(type)) {
                return type;
            }
        }

        return '';
    }

    async start(): Promise<void> {
        this.stopped = false;
        this.chunks = [];
        this.amplitude = [];

        this.stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });

        const mimeType = VoiceRecorder.pickMimeType();
        this.recorder = mimeType
            ? new MediaRecorder(this.stream, { mimeType })
            : new MediaRecorder(this.stream);

        this.recorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                this.chunks.push(e.data);
            }
        };

        this.recorder.start(250);
        this.startedAt = performance.now();

        // Amplitude analysis for the live waveform
        this.ctx = new AudioContext();
        const source = this.ctx.createMediaStreamSource(this.stream);
        this.analyser = this.ctx.createAnalyser();
        this.analyser.fftSize = 512;
        source.connect(this.analyser);

        const buf = new Uint8Array(this.analyser.frequencyBinCount);
        let lastTickAt = 0;

        const loop = () => {
            if (this.stopped || !this.analyser) return;

            this.analyser.getByteTimeDomainData(buf);

            let peak = 0;
            for (let i = 0; i < buf.length; i++) {
                const v = Math.abs(buf[i] - 128) / 128;
                if (v > peak) peak = v;
            }

            this.onAmplitude?.(peak);
            this.onTick?.((performance.now() - this.startedAt) / 1000);

            const now = performance.now();
            if (now - lastTickAt > 60) {
                this.amplitude.push(peak);
                lastTickAt = now;
            }

            this.rafId = requestAnimationFrame(loop);
        };

        this.rafId = requestAnimationFrame(loop);
    }

    /**
     * Stops recording and returns the result.
     * Returns null when nothing was captured (too short / denied).
     */
    async stop(): Promise<VoiceRecording | null> {
        this.stopped = true;

        if (this.rafId !== null) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }

        const durationSec = (performance.now() - this.startedAt) / 1000;

        const blob = await new Promise<Blob>((resolve) => {
            if (!this.recorder) {
                resolve(new Blob());
                return;
            }

            const rec = this.recorder;

            if (rec.state === 'inactive') {
                resolve(new Blob(this.chunks));
                return;
            }

            rec.onstop = () => resolve(new Blob(this.chunks));
            rec.stop();
        });

        this.cleanup();

        if (blob.size === 0 || durationSec < 0.4) {
            return null;
        }

        // Resample amplitude track to a fixed bar count
        const waveform = resample(this.amplitude, TARGET_SAMPLES);

        return { blob, durationSec, waveform };
    }

    /** Cancels without returning a recording. */
    async cancel(): Promise<void> {
        this.stopped = true;

        if (this.rafId !== null) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }

        if (this.recorder && this.recorder.state !== 'inactive') {
            this.recorder.onstop = null;
            this.recorder.stop();
        }

        this.cleanup();
    }

    private cleanup(): void {
        this.stream?.getTracks().forEach((t) => t.stop());
        this.stream = null;
        this.recorder = null;

        void this.ctx?.close().catch(() => undefined);
        this.ctx = null;
        this.analyser = null;
    }
}

function resample(input: number[], target: number): number[] {
    if (input.length === 0) {
        return new Array(target).fill(0.08);
    }

    const out: number[] = [];

    for (let i = 0; i < target; i++) {
        const from = Math.floor((i / target) * input.length);
        const to = Math.max(from + 1, Math.floor(((i + 1) / target) * input.length));
        let peak = 0;

        for (let j = from; j < to && j < input.length; j++) {
            peak = Math.max(peak, input[j]);
        }

        out.push(peak);
    }

    return out;
}

export function formatVoiceDuration(sec: number): string {
    if (!Number.isFinite(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}
