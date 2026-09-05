<script lang="ts">
    import type {
        Message
    } from '$lib/types/message';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        resolveAttachmentUrl
    } from '$lib/utils/attachments';

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

    let {
        message
    }: {
        message: Message;
    } = $props();

    let type = $derived(
        message.content_type ?? 'text'
    );

    let url = $derived(
        resolveAttachmentUrl(
            message.media_url,
            roomsState.roomToken
        )
    );
</script>

{#if url && type !== 'text'}
    {#if type === 'image' || type === 'gif'}
        <div class="msg-media">
            <img
                src={url}
                alt={
                    message.file_name ||
                    t('attachmentLabel')
                }
                loading="lazy"
            />
        </div>

    {:else if type === 'video'}
        <div class="msg-media">
            <!-- svelte-ignore a11y_media_has_caption -->
            <video
                src={url}
                controls
                preload="metadata"
            >
            </video>
        </div>

    {:else}
        <div class="msg-file">
            <div class="msg-file-icon">
                <Icon
                    name={fileIconName(
                        message.mime_type ||
                            message.file_name ||
                            ''
                    )}
                    size={30}
                />
            </div>

            <div class="msg-file-info">
                <div class="msg-file-name">
                    {message.file_name ||
                        t('attachmentLabel')}
                </div>

                <div class="msg-file-meta">
                    {[
                        message.mime_type,

                        message.file_size != null
                            ? formatBytes(
                                message.file_size
                            )
                            : ''
                    ]
                        .filter(Boolean)
                        .join(' | ') ||
                        t('fileLabel')}
                </div>
            </div>

            <a
                class="file-link"
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                download={message.file_name}
            >
                <Icon
                    name="download"
                    size={15}
                />

                {t('download')}
            </a>
        </div>
    {/if}
{/if}