import type {
    Message
} from '$lib/types/message';

import type {
    TranslationKey,
    TranslationVars
} from '$lib/i18n/translations';

class ComposerState {
    text = $state('');

    /** True while the voice recorder UI is active (input hides). */
    voiceRecording = $state(false);

    replyTarget =
        $state<Message | null>(null);

    pendingFile =
        $state<File | null>(null);

    pendingUrl = $state('');

    uploading = $state(false);

    uploadProgress = $state(0);

    private cancelUploadFn:
        | (() => void)
        | null = null;

    registerUploadCanceller(
        cancel: () => void
    ): void {
        this.cancelUploadFn = cancel;
    }

    clearUploadCanceller(): void {
        this.cancelUploadFn = null;
    }

    cancelUpload(): boolean {
        if (
            this.cancelUploadFn &&
            this.uploading
        ) {
            this.cancelUploadFn();

            return true;
        }

        return false;
    }

    statusKey =
        $state<TranslationKey | null>(null);

    statusVars =
        $state<TranslationVars>({});

    statusError =
        $state<unknown>(null);

    statusFallback =
        $state<TranslationKey | null>(null);

    statusIsError = $state(false);

    setReply(
        message: Message
    ): void {
        this.replyTarget = message;
    }

    clearReply(): void {
        this.replyTarget = null;
    }

    setPendingFile(
        file: File
    ): void {
        this.clearPendingFile();

        this.pendingFile = file;

        if (
            file.type.startsWith('image/') ||
            file.type.startsWith('video/')
        ) {
            this.pendingUrl =
                URL.createObjectURL(file);
        }
    }

    clearPendingFile(): void {
        if (this.pendingUrl) {
            URL.revokeObjectURL(
                this.pendingUrl
            );
        }

        this.pendingUrl = '';
        this.pendingFile = null;
    }

    setStatus(
        key: TranslationKey,
        vars: TranslationVars = {},
        error = false
    ): void {
        this.statusKey = key;
        this.statusVars = vars;

        this.statusError = null;
        this.statusFallback = null;

        this.statusIsError = error;
    }

    setApiError(
        error: unknown,
        fallback: TranslationKey
    ): void {
        this.statusError = error;
        this.statusFallback = fallback;

        this.statusKey = null;
        this.statusVars = {};

        this.statusIsError = true;
    }

    clearStatus(): void {
        this.statusKey = null;
        this.statusVars = {};

        this.statusError = null;
        this.statusFallback = null;

        this.statusIsError = false;
    }

    reset(): void {
        this.text = '';

        this.clearReply();
        this.clearPendingFile();
        this.clearStatus();

        this.uploading = false;
        this.uploadProgress = 0;
        this.cancelUploadFn = null;
    }
}

export const composerState =
    new ComposerState();