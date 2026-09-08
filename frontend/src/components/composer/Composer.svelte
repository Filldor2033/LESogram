<script lang="ts">
    import {
        onDestroy,
        tick
    } from 'svelte';

    import {
        authState
    } from '$lib/state/auth.svelte';

    import {
        chatState
    } from '$lib/state/chat.svelte';

    import {
        composerState
    } from '$lib/state/composer.svelte';

    import {
        roomUsersState
    } from '$lib/state/room-users.svelte';

    import {
        sendAttachment
    } from '$lib/api/attachments';

    import VoiceRecorderButton
        from './VoiceRecorderButton.svelte';

    import {
        sendRealtime
    } from '$lib/realtime/websocket';

    import {
        getMentionQuery
    } from '$lib/utils/mentions';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import Icon
        from '$components/common/Icon.svelte';

    import ReplyPreview
        from './ReplyPreview.svelte';

    import AttachmentPreview
        from './AttachmentPreview.svelte';

    import MentionDropdown
        from './MentionDropdown.svelte';

    let inputElement:
        HTMLInputElement;

    let attachmentInput:
        HTMLInputElement;

    let cursor = $state(0);

    let mentionIndex = $state(0);

    let typingTimer:
        number | null = null;

    let mention = $derived(
        getMentionQuery(
            composerState.text,
            cursor
        )
    );

    let mentionUsers = $derived.by(() => {
        if (!mention) {
            return [];
        }

        return roomUsersState.users
            .map(user => user.username)
            .filter(
                username =>
                    username !==
                        authState.username &&
                    username
                        .toLowerCase()
                        .includes(
                            mention!.query
                        )
            )
            .slice(0, 8);
    });

    function updateCursor() {
        cursor =
            inputElement
                ?.selectionStart ??
            composerState.text.length;
    }

    function sendTyping(
        typing: boolean
    ) {
        if (
            chatState.realtime !==
            'open'
        ) {
            return;
        }

        sendRealtime({
            type: 'typing',
            is_typing: typing
        });
    }

    function handleInput() {
        updateCursor();

        mentionIndex = 0;

        composerState.clearStatus();

        sendTyping(true);

        if (typingTimer != null) {
            clearTimeout(
                typingTimer
            );
        }

        typingTimer =
            window.setTimeout(
                () => {
                    sendTyping(false);
                    typingTimer = null;
                },
                1200
            );
    }

    async function insertMention(
        username: string
    ) {
        const current =
            getMentionQuery(
                composerState.text,
                cursor
            );

        if (!current) {
            return;
        }

        const before =
            composerState.text.slice(
                0,
                current.start
            );

        const after =
            composerState.text.slice(
                current.end
            );

        composerState.text =
            `${before}@${username} ${after}`;

        const nextCursor =
            before.length +
            username.length +
            2;

        await tick();

        inputElement.focus();

        inputElement
            .setSelectionRange(
                nextCursor,
                nextCursor
            );

        cursor = nextCursor;
    }

    async function sendPendingFile() {
        const file =
            composerState.pendingFile;

        if (
            !file ||
            !chatState.active
        ) {
            return;
        }

        const form =
            new FormData();

        form.append(
            'room_token',
            chatState.roomToken
        );

        form.append(
            'text',
            composerState.text.trim()
        );

        form.append(
            'file',
            file
        );

        if (
            composerState
                .replyTarget?.id
        ) {
            form.append(
                'reply_to_id',
                String(
                    composerState
                        .replyTarget.id
                )
            );
        }

        composerState.uploading = true;
        composerState.uploadProgress = 0;

        composerState.setStatus(
            'uploadingFile',
            {
                file: file.name
            }
        );

        try {
            const message =
                await sendAttachment(
                    authState.token,
                    chatState.room,
                    form,
                    (fraction) => {
                        composerState.uploadProgress =
                            Math.round(
                                fraction *
                                100
                            );
                    },
                    (cancel) => {
                        composerState
                            .registerUploadCanceller(
                                cancel
                            );
                    }
                );

            /*
             * Если WS уже прислал это сообщение,
             * chatState.append() сделает replace,
             * а не дубль.
             */
            chatState.append(message);

            const name = file.name;

            composerState.text = '';
            composerState.clearReply();
            composerState.clearPendingFile();

            composerState.setStatus(
                'fileSent',
                { file: name }
            );
        } catch (error) {
            if (
                error instanceof
                    DOMException &&
                error.name ===
                    'AbortError'
            ) {
                /*
                 * User cancelled: keep the file in the
                 * preview so it can be retried.
                 */
                composerState.setStatus(
                    'uploadCancelled',
                    {
                        file: file.name
                    }
                );
            } else {
                composerState.setApiError(
                    error,
                    'uploadFailed'
                );
            }
        } finally {
            composerState.uploading =
                false;

            composerState.uploadProgress =
                0;

            composerState
                .clearUploadCanceller();
        }
    }

    async function sendVoice(
        blob: Blob,
        durationSec: number,
        waveform?: number[]
    ) {
        if (!chatState.active) return;

        const ext = blob.type.includes('ogg')
            ? 'ogg'
            : blob.type.includes('wav')
              ? 'wav'
              : 'webm';

        const file = new File(
            [blob],
            `voice_${Date.now()}.${ext}`,
            { type: blob.type }
        );

        const form = new FormData();

        form.append(
            'room_token',
            chatState.roomToken
        );

        form.append('text', '');

        form.append(
            'voice_duration',
            String(Math.round(durationSec * 10) / 10)
        );

        if (waveform && waveform.length > 0) {
            form.append(
                'voice_waveform',
                JSON.stringify(
                    waveform.map((v) => Math.round(v * 100) / 100)
                )
            );
        }

        form.append('file', file);

        if (composerState.replyTarget?.id) {
            form.append(
                'reply_to_id',
                String(composerState.replyTarget.id)
            );
        }

        composerState.uploading = true;
        composerState.uploadProgress = 0;
        composerState.setStatus('sendingVoice');

        try {
            const message = await sendAttachment(
                authState.token,
                chatState.room,
                form
            );

            chatState.append(message);
            composerState.clearReply();
            composerState.setStatus('voiceSent');
        } catch (error) {
            if (
                error instanceof Error &&
                error.name === 'AbortError'
            ) {
                composerState.setStatus('uploadCancelled');
            } else {
                composerState.setStatus(
                    'voiceSendFailed',
                    {},
                    true
                );
                throw error;
            }
        } finally {
            composerState.uploading = false;
            composerState.uploadProgress = 0;
        }
    }

    function onVoiceError(key: string) {
        composerState.setStatus(
            key as never,
            {},
            true
        );
    }

    async function send() {
        if (!chatState.active) {
            composerState.setStatus(
                'joinRoomFirst',
                {},
                true
            );

            return;
        }

        if (
            composerState.pendingFile
        ) {
            await sendPendingFile();
            return;
        }

        if (
            chatState.realtime !==
            'open'
        ) {
            composerState.setStatus(
                'realtimeNotReady',
                {},
                true
            );

            return;
        }

        const text =
            composerState.text.trim();

        if (!text) {
            return;
        }

        const sent =
            sendRealtime({
                text,

                reply_to_id:
                    composerState
                        .replyTarget?.id ??
                    null
            });

        if (!sent) {
            composerState.setStatus(
                'realtimeNotReady',
                {},
                true
            );

            return;
        }

        composerState.text = '';

        composerState.clearReply();
        composerState.clearStatus();

        sendTyping(false);

        if (typingTimer != null) {
            clearTimeout(
                typingTimer
            );

            typingTimer = null;
        }
    }

    function handleKeydown(
        event: KeyboardEvent
    ) {
        if (mentionUsers.length) {
            if (
                event.key ===
                'ArrowDown'
            ) {
                event.preventDefault();

                mentionIndex =
                    (mentionIndex + 1) %
                    mentionUsers.length;

                return;
            }

            if (
                event.key ===
                'ArrowUp'
            ) {
                event.preventDefault();

                mentionIndex =
                    (
                        mentionIndex -
                        1 +
                        mentionUsers.length
                    ) %
                    mentionUsers.length;

                return;
            }

            if (
                event.key === 'Enter' ||
                event.key === 'Tab'
            ) {
                event.preventDefault();

                void insertMention(
                    mentionUsers[
                        mentionIndex
                    ]
                );

                return;
            }

            if (
                event.key ===
                'Escape'
            ) {
                mentionIndex = 0;
                cursor = -1;

                return;
            }
        }

        if (
            event.key === 'Enter' &&
            !event.shiftKey
        ) {
            event.preventDefault();

            void send();
        }
    }

    function selectAttachment(
        event: Event
    ) {
        const element = event.currentTarget;

        if (!(element instanceof HTMLInputElement)) {
            return;
        }

        const file =
            element.files?.[0];

        element.value = '';

        if (!file) {
            return;
        }

        if (!chatState.active) {
            composerState.setStatus(
                'joinRoomFirst',
                {},
                true
            );

            return;
        }

        composerState
            .setPendingFile(file);

        inputElement?.focus();
    }

    onDestroy(() => {
        sendTyping(false);

        if (typingTimer != null) {
            clearTimeout(
                typingTimer
            );
        }
    });
</script>

<div class="composer">
    <div class="composer-tools"></div>

    <ReplyPreview />

    <MentionDropdown
        users={mentionUsers}
        activeIndex={mentionIndex}
        onSelect={insertMention}
    />

    <AttachmentPreview />

    <div class="input-row">
        <button
            class="secondary tool-btn attach-btn"
            style="max-width:40px"
            type="button"
            disabled={!chatState.active}
            title={t('pickFile')}
            aria-label={t('pickFile')}
            onclick={() =>
                attachmentInput.click()}
        >
            <Icon
                name="paperclip"
                size={17}
            />
        </button>

        <VoiceRecorderButton
            disabled={!chatState.active}
            onSend={(blob, dur, wave) =>
                void sendVoice(blob, dur, wave)}
            onError={onVoiceError}
        />

        <input
            id="message-input"
            bind:this={inputElement}
            bind:value={composerState.text}
            disabled={!chatState.active}
            placeholder={
                t('messagePlaceholder')
            }
            oninput={handleInput}
            onclick={updateCursor}
            onkeyup={updateCursor}
            onkeydown={handleKeydown}
        />

        <button
            class="send-btn"
            type="button"
            disabled={
                !chatState.active ||
                composerState.uploading
            }
            onclick={() => void send()}
        >
            <Icon
                name="send"
                size={16}
            />

            {t('send')}
        </button>
    </div>

    <div
        class="status composer-status"
        class:error={
            composerState.statusIsError
        }
    >
        {#if
            composerState.statusError &&
            composerState.statusFallback
        }
            {getApiErrorMessage(
                composerState.statusError,
                composerState.statusFallback
            )}

        {:else if composerState.statusKey}
            {t(
                composerState.statusKey,
                composerState.statusVars
            )}

        {:else if
            chatState.active &&
            chatState.realtime === 'closed'
        }
            {t('realtimeClosed')}
        {/if}
    </div>

    <input
        bind:this={attachmentInput}
        class="hidden"
        type="file"
        onchange={selectAttachment}
    />
</div>