/**
 * Runtime API base for the LESogram client.
 *
 * Web (same origin):  relative '/api' requests — nothing changes.
 * Android app (Capacitor WebView): the app is served from a local
 * scheme, so every request must target the production server
 * absolutely. The URL is baked at BUILD time via VITE_API_BASE
 * (see mobile builds) — runtime detection keeps the web build
 * untouched.
 */

function resolveApiBase(): string {
    const injected = import.meta.env.VITE_API_BASE as string | undefined;

    if (injected) {
        // trim trailing slash; no scheme-relative hosts
        return injected.replace(/\/+$/, '');
    }

    /*
     * Capacitor WebView: https://localhost or capacitor://localhost.
     * The Capacitor runtime is injected by the native shell — declare
     * it loosely, the web build never ships it.
     */
    const cap = (
        window as unknown as {
            Capacitor?: { isNativePlatform?: () => boolean };
        }
    ).Capacitor;

    if (cap?.isNativePlatform?.()) {
        return 'https://lesogram.ru';
    }

    return '';
}

export const API_BASE = resolveApiBase();

export const API_PREFIX = `${API_BASE}/api`;
