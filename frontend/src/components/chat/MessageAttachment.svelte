<script lang="ts">
    import type {
        Message
    } from '$lib/types/message';

    import {
        roomsState
    } from '$lib/state/rooms.svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

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

    import VideoPlayer
        from '$components/chat/VideoPlayer.svelte';

    import Lightbox
        from '$components/chat/Lightbox.svelte';

    let {
        message
    }: {
        message: Message;
    } = $props();

    let lightboxOpen = $state(false);

    let type = $derived(
        message.content_type ?? 'text'
    );

    let url = $derived(
        resolveAttachmentUrl(
            message.media_url,
            roomsState.roomToken
        )
    );

    // All images in the current chat, for lightbox navigation
    let galleryImages = $derived(
        chatState.messages
            .filter(
                (m) =>
                    (m.content_type === 'image' ||
                        m.content_type === 'gif') &&
                    m.media_url
            )
            .map((m) => ({
                url: resolveAttachmentUrl(
                    m.media_url,
                    roomsState.roomToken
                ),
                name: m.file_name
            }))
    );

    let galleryIndex = $derived(
        galleryImages.findIndex(
            (g) => g.url === url
        )
    );
</script>

{#if url && type !== 'text'}
    {#if type === 'image' || type === 'gif'}
        <div class="msg-media">
            <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <img
                src={url}
                alt={
                    message.file_name ||
                    t('attachmentLabel')
                }
                loading="lazy"
                onclick={() => (lightboxOpen = true)}
            />
        </div>

        {#if lightboxOpen}
            {#key url}
                <Lightbox
                    images={galleryImages}
                    index={Math.max(0, galleryIndex)}
                    onclose={() => (lightboxOpen = false)}
                />
            {/key}
        {/if}

    {:else if type === 'video'}
        <div class="msg-media">
            <VideoPlayer
                src={url}
                file_name={message.file_name}
            />
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
