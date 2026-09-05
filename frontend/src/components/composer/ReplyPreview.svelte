<script lang="ts">
    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        getReplyPreview
    } from '$lib/utils/messages';

    import {
        t
    } from '$lib/i18n/i18n.svelte';
</script>

{#if composerState.replyTarget}
    <div class="reply-preview">
        <div>
            <div class="reply-preview-title">
                {composerState.replyTarget.username ||
                    t('reply')}
            </div>

            <div class="reply-preview-text">
                {getReplyPreview(
                    composerState.replyTarget
                )}
            </div>
        </div>

        <button
            type="button"
            class="reply-preview-close"
            title={t('close')}
            aria-label={t('close')}
            onclick={() =>
                composerState.clearReply()}
        >
            ×
        </button>
    </div>
{/if}