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

            {#if composerState.uploading}
                <div
                    class="upload-progress"
                    role="progressbar"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-valuenow={
                        composerState
                            .uploadProgress
                    }
                >
                    <div
                        class="upload-progress-track"
                    >
                        <div
                            class="upload-progress-fill"
                            style={`width:${
                                composerState
                                    .uploadProgress
                            }%`}
                        >
                            <div
                                class="upload-progress-shine"
                            ></div>
                        </div>
                    </div>

                    <span
                        class="upload-progress-label"
                    >
                        {composerState
                            .uploadProgress}%
                    </span>
                </div>
            {/if}
        </div>

        <div class="upload-preview-actions">
            {#if !composerState.uploading}
                <button
                    type="button"
                    class="secondary small-btn"
                    onclick={() =>
                        composerState
                            .clearPendingFile()}
                >
                    {t('cancel')}
                </button>
            {/if}
        </div>
    </div>
{/if}