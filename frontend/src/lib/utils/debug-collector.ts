/**
 * Console/error collector for the debug build.
 *
 * Mirrors console.log/warn/error and window errors into a ring
 * buffer; the debug bar can POST everything to /api/debug-report
 * so a failing voice recording on Android (no devtools there)
 * can be diagnosed from the server side.
 */

import { isNativeApp } from '$lib/utils/platform';

const LIMIT = 300;

type Entry = {
    at: number;
    level: 'log' | 'warn' | 'error';
    args: string[];
};

const entries: Entry[] = [];

function fmt(value: unknown): string {
    if (typeof value === 'string') {
        return value;
    }

    try {
        return JSON.stringify(value);
    } catch {
        return String(value);
    }
}

function push(level: Entry['level'], args: unknown[]): void {
    entries.push({
        at: Date.now(),
        level,
        args: args.map(fmt).slice(0, 12)
    });

    if (entries.length > LIMIT) {
        entries.splice(0, entries.length - LIMIT);
    }
}

/*
 * Only hook the console inside the native app — the web build
 * keeps its pristine console (the module is imported by
 * DebugBar which renders nothing on the web).
 */
if (isNativeApp()) {
    const original = {
        log: console.log.bind(console),
        warn: console.warn.bind(console),
        error: console.error.bind(console)
    };

    console.log = (...args: unknown[]) => {
        push('log', args);
        original.log(...args);
    };

    console.warn = (...args: unknown[]) => {
        push('warn', args);
        original.warn(...args);
    };

    console.error = (...args: unknown[]) => {
        push('error', args);
        original.error(...args);
    };

    window.addEventListener('error', (event) => {
        push('error', [
            `[window] ${event.message} @ ${event.filename}:${event.lineno}`
        ]);
    });

    window.addEventListener(
        'unhandledrejection',
        (event) => {
            push('error', [
                `[promise] ${fmt(event.reason)}`
            ]);
        }
    );
}

export function debugEntries(): Entry[] {
    return entries;
}

export async function sendDebugReport(): Promise<'sent' | 'failed'> {
    const diagnostics = {
        ua: navigator.userAgent,
        secure: window.isSecureContext,
        platform: 'native',
        notificationApi: 'Notification' in window,
        mediaDevices: !!navigator.mediaDevices?.getUserMedia,
        mediaRecorder: typeof MediaRecorder !== 'undefined',
        mimeTypes: [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/ogg',
            'audio/mp4'
        ].filter((t) => {
            try {
                return MediaRecorder.isTypeSupported?.(t) === true;
            } catch {
                return false;
            }
        })
    };

    try {
        const base = (
            window as unknown as {
                Capacitor?: {
                    Plugins?: Record<string, unknown>;
                };
            }
        ).Capacitor;

        const server = 'https://lesogram.ru';

        const response = await fetch(
            `${server}/api/debug-report`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ua: navigator.userAgent,
                    platform: 'native',
                    entries,
                    diagnostics
                })
            }
        );

        return response.ok ? 'sent' : 'failed';
    } catch {
        return 'failed';
    }
}
