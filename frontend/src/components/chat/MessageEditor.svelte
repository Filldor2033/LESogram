<script lang="ts">
    import {
        messageActions
    } from '$lib/services/message-actions.svelte';

    import {
        t
    } from '$lib/i18n/i18n.svelte';

    import type {
        Message
    } from '$lib/types/message';

    let {
        message
    }: {
        message: Message;
    } = $props();

    let text =
        // svelte-ignore state_referenced_locally
        $state(message.text ?? '');

    let saving = $state(false);

    async function save() {
        if (!message.id) {
            return;
        }

        saving = true;

        try {
            await messageActions
                .saveEdit(
                    message.id,
                    text
                );
        } finally {
            saving = false;
        }
    }
</script>

<div class="msg-editor">
    <textarea
        class="msg-editor-input"
        bind:value={text}
    ></textarea>

    <div class="msg-editor-actions">
        <button
            class="small-btn"
            type="button"
            disabled={saving}
            onclick={() => void save()}
        >
            {t('save')}
        </button>

        <button
            class="secondary small-btn"
            type="button"
            onclick={() =>
                messageActions.cancelEdit()}
        >
            {t('cancel')}
        </button>
    </div>
</div>