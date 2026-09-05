<script lang="ts">
    import type {
        Message
    } from '$lib/types/message';

    import {
        getSystemMessageText
    } from '$lib/utils/messages';

    let {
        message
    }: {
        message: Message;
    } = $props();
</script>

<div class="msg system">
    {getSystemMessageText(message)}
</div>