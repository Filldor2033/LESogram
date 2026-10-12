/**
 * Runtime platform detection. The Capacitor runtime is injected
 * only by the native Android shell — the web build never sees it.
 */

export function isNativeApp(): boolean {
    if (typeof window === 'undefined') {
        return false;
    }

    const cap = (
        window as unknown as {
            Capacitor?: {
                isNativePlatform?: () => boolean;
            };
        }
    ).Capacitor;

    return Boolean(
        cap?.isNativePlatform?.()
    );
}
