<script lang="ts">
    import { isNativeApp } from '$lib/utils/platform';
    import { sendDebugReport } from '$lib/utils/debug-collector';

    let reportState = $state('idle');
    let busy = $state(false);

    function report(): void {
        busy = true;

        void sendDebugReport().then((result) => {
            reportState = result;

            window.setTimeout(() => {
                reportState = 'idle';
            }, 4000);

            busy = false;
        });
    }
</script>

{#if isNativeApp()}
    <div class="debug-bar">
        <span class="debug-dot"></span>
        <span class="debug-label">debug</span>

        <button
            class="small-btn"
            type="button"
            disabled={busy}
            onclick={report}
        >
            {#if busy}
                …
            {:else if reportState === 'sent'}
                ✓ sent
            {:else if reportState === 'failed'}
                ✗ failed
            {:else}
                send report
            {/if}
        </button>
    </div>
{/if}

<style>
    .debug-bar {
        position: fixed;
        left: 50%;
        bottom: 0;
        transform: translateX(-50%);

        display: flex;
        align-items: center;
        gap: 8px;

        padding: 4px 10px;
        border-radius: 10px 10px 0 0;

        background: rgba(2, 6, 23, 0.92);
        border: 1px solid rgba(34, 197, 94, 0.4);
        border-bottom: none;

        font-size: 11px;
        color: rgba(148, 163, 184, 0.9);

        z-index: 9999;
    }

    .debug-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        animation: debugPulse 1.6s infinite;
    }

    @keyframes debugPulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }

    .debug-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .small-btn {
        min-height: 24px;
        padding: 2px 10px;
        font-size: 11px;
    }
</style>
