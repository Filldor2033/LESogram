<script lang="ts">
    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        formatBytes
    } from '$lib/utils/files';

    import {
        fileIconName
    } from '$lib/icons';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import Icon
        from '$components/common/Icon.svelte';

    let file = $derived(
        composerState.pendingFile
    );
</script>

{#if file}
    <div class="upload-preview">
        <div class="upload-preview-media">
            {#if
                file.type.startsWith('image/') &&
                composerState.pendingUrl
            }
                <img
                    src={composerState.pendingUrl}
                    alt={file.name}
                />

            {:else if
                file.type.startsWith('video/') &&
                composerState.pendingUrl
            }
                <video
                    src={composerState.pendingUrl}
                    muted
                    playsinline
                >
                </video>

            {:else}
                <div class="upload-file-preview">
                    <div class="upload-file-icon">
                        <Icon
                            name={fileIconName(
                                file.type ||
                                    file.name
                            )}
                            size={26}
                        />
                    </div>
                </div>
            {/if}
        </div>

        <div class="upload-preview-info">
            <div class="upload-preview-name">
                {file.name}
            </div>

            <div class="upload-preview-meta">
                {[
                    file.type || t('fileLabel'),
                    formatBytes(file.size)
                ]
                    .filter(Boolean)
                    .join(' | ')}
            </div>
        </div>

        <div class="upload-preview-actions">
            <button
                type="button"
                class="secondary small-btn"
                onclick={() =>
                    composerState
                        .clearPendingFile()}
            >
                {t('cancel')}
            </button>
        </div>
    </div>
{/if}