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
    private intervalId: number | null = null;
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

    /**
     * True when the page itself cannot access media devices at all
     * (plain HTTP on a non-localhost origin).
     */
    static get insecureContext(): boolean {
        return (
            typeof window !== 'undefined' &&
            !window.isSecureContext
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
        this.pausedTotal = 0;

        this.setupAnalyser();
    }

    private setupAnalyser(): void {
        // Amplitude analysis for the live waveform.
        // setInterval (not rAF): rAF is throttled when the tab is
        // backgrounded, which froze the timer and the waveform.
        this.ctx = new AudioContext();
        const source = this.ctx.createMediaStreamSource(this.stream!);
        this.analyser = this.ctx.createAnalyser();
        this.analyser.fftSize = 512;
        source.connect(this.analyser);

        const buf = new Uint8Array(this.analyser.frequencyBinCount);
        let lastTickAt = 0;

        this.intervalId = window.setInterval(() => {
            if (this.stopped || !this.analyser) return;

            if (!this.paused) {
                this.analyser.getByteTimeDomainData(buf);

                let peak = 0;
                for (let i = 0; i < buf.length; i++) {
                    const v = Math.abs(buf[i] - 128) / 128;
                    if (v > peak) peak = v;
                }

                this.onAmplitude?.(peak);
                this.onTick?.(
                    (performance.now() - this.startedAt - this.pausedTotal) / 1000
                );

                const now = performance.now();
                if (now - lastTickAt > 60) {
                    this.amplitude.push(peak);
                    lastTickAt = now;
                }
            }
        }, 50);
    }

    paused = false;
    private pauseStartedAt = 0;
    private pausedTotal = 0;

    /** Pauses recording (timer and amplitude freeze). */
    pause(): void {
        if (this.paused || !this.recorder || this.recorder.state !== 'recording') return;

        this.paused = true;
        this.pauseStartedAt = performance.now();

        try {
            this.recorder.pause();
        } catch {
            // recorder doesn't support pause — keep amplitude freeze anyway
        }
    }

    /** Resumes a paused recording. */
    resume(): void {
        if (!this.paused) return;

        this.pausedTotal += performance.now() - this.pauseStartedAt;
        this.paused = false;

        try {
            this.recorder?.resume();
        } catch {
            // ignore
        }
    }

    /**
     * Stops recording and returns the result.
     * Returns null when nothing was captured (too short / denied).
     */
    async stop(): Promise<VoiceRecording | null> {
        this.stopped = true;

        if (this.intervalId !== null) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        // Exclude paused time: the recorded audio contains no
        // paused segments, so the duration must not count them.
        const durationSec =
            (performance.now() - this.startedAt - this.pausedTotal) / 1000;

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

            let settled = false;

            const finish = () => {
                if (settled) return;
                settled = true;
                resolve(new Blob(this.chunks));
            };

            rec.onstop = finish;
            rec.onerror = finish;

            // Safety net: if onstop never fires (browser quirk),
            // resolve with whatever chunks exist after 2s.
            const timeout = window.setTimeout(finish, 2000);

            const clear = () => window.clearTimeout(timeout);
            rec.onstop = () => {
                clear();
                finish();
            };

            // Chrome drops buffered data when stop() is called on a
            // paused recorder — resume first, then stop.
            if (rec.state === 'paused') {
                try {
                    rec.resume();
                } catch {
                    // ignore — stop() anyway
                }
            }

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

        if (this.intervalId !== null) {
            clearInterval(this.intervalId);
            this.intervalId = null;
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

/**
 * Resamples an amplitude track to a fixed bar count. Public wrapper
 * for the pause-time segment waveform.
 */
export function resampleWave(input: number[], target: number): number[] {
    return resample(input, target);
}

/**
 * Decodes blobs to PCM, concatenates them end-to-end and re-encodes
 * as one mono WAV. Returns null when any blob fails to decode (the
 * caller falls back to the last part).
 */
export async function concatVoiceToWav(blobs: Blob[]): Promise<Blob | null> {
    if (blobs.length === 0) return null;

    try {
        const ctx = new AudioContext();

        const buffers: AudioBuffer[] = [];

        for (const blob of blobs) {
            const buf = await blob.arrayBuffer();
            buffers.push(await ctx.decodeAudioData(buf.slice(0)));
        }

        const sampleRate = buffers[0].sampleRate;
        let total = 0;

        for (const b of buffers) {
            total += b.length;
        }

        const mono = new Float32Array(total);

        let offset = 0;

        for (const b of buffers) {
            const channels = Math.min(2, b.numberOfChannels);

            for (let ch = 0; ch < channels; ch++) {
                const data = b.getChannelData(ch);

                for (let i = 0; i < b.length; i++) {
                    mono[offset + i] += data[i] / channels;
                }
            }

            offset += b.length;
        }

        void ctx.close();

        return encodeWav(mono, sampleRate);
    } catch {
        return null;
    }
}

/**
 * Trims a recorded blob to [fromSec, toSec] and re-encodes as WAV.
 * Returns null when trimming is unnecessary or fails.
 */
export async function trimVoiceToWav(
    blob: Blob,
    fromSec: number,
    toSec: number
): Promise<Blob | null> {
    try {
        const arrayBuffer = await blob.arrayBuffer();
        const ctx = new AudioContext();
        const audioBuffer = await ctx.decodeAudioData(arrayBuffer.slice(0));

        const duration = audioBuffer.duration;

        // Nothing to trim — keep the original
        if (fromSec <= 0.01 && toSec >= duration - 0.01) {
            void ctx.close();
            return null;
        }

        const startSample = Math.max(0, Math.floor(fromSec * audioBuffer.sampleRate));
        const endSample = Math.min(
            audioBuffer.length,
            Math.ceil(toSec * audioBuffer.sampleRate)
        );

        if (endSample - startSample < audioBuffer.sampleRate * 0.3) {
            void ctx.close();
            throw new Error('trimmed-too-short');
        }

        // Mix down to mono for smaller files
        const channels = Math.min(2, audioBuffer.numberOfChannels);
        const outLength = endSample - startSample;
        const mono = new Float32Array(outLength);

        for (let ch = 0; ch < channels; ch++) {
            const data = audioBuffer.getChannelData(ch);
            for (let i = 0; i < outLength; i++) {
                mono[i] += data[startSample + i] / channels;
            }
        }

        void ctx.close();

        return encodeWav(mono, audioBuffer.sampleRate);
    } catch (err) {
        if (err instanceof Error && err.message === 'trimmed-too-short') {
            throw err;
        }
        return null;
    }
}

/** Minimal 16-bit PCM WAV encoder. */
function encodeWav(samples: Float32Array, sampleRate: number): Blob {
    const bytesPerSample = 2;
    const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
    const view = new DataView(buffer);

    const writeString = (offset: number, s: string) => {
        for (let i = 0; i < s.length; i++) {
            view.setUint8(offset + i, s.charCodeAt(i));
        }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * bytesPerSample, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * bytesPerSample, true);
    view.setUint16(32, bytesPerSample, true);
    view.setUint16(34, 16, true); // bits per sample
    writeString(36, 'data');
    view.setUint32(40, samples.length * bytesPerSample, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
        offset += bytesPerSample;
    }

    return new Blob([buffer], { type: 'audio/wav' });
}

export function formatVoiceDuration(sec: number): string {
    if (!Number.isFinite(sec)) return '0:00';
    // Round to nearest: a 1.8s recording should show 0:02, not 0:01
    // (floor clipped nearly a full second off trimmed messages).
    const total = Math.round(sec);
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}
