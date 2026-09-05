import {
    request
} from '$lib/api/http';

import type {
    Message
} from '$lib/types/message';

export function sendAttachment(
    token: string,
    room: string,
    formData: FormData,
    onProgress?:
        (fraction: number) => void,
    registerCanceller?: (
        cancel: () => void
    ) => void
): Promise<Message> {
    /*
     * fetch() cannot report upload progress; an XHR can.
     * Falls back to request() when no progress callback is
     * given (same error handling path).
     */
    if (!onProgress) {
        return request<Message>(
            `/rooms/${encodeURIComponent(room)}/attachments`,
            {
                method: 'POST',

                headers: {
                    Authorization:
                        `Bearer ${token}`
                },

                body: formData
            }
        );
    }

    return new Promise<Message>(
        (resolve, reject) => {
            const xhr =
                new XMLHttpRequest();

            registerCanceller?.(
                () => xhr.abort()
            );

            xhr.open(
                'POST',
                `/api/rooms/${encodeURIComponent(room)}/attachments`
            );

            xhr.setRequestHeader(
                'Authorization',
                `Bearer ${token}`
            );

            xhr.upload.onprogress = (
                event
            ) => {
                if (
                    event.lengthComputable
                ) {
                    onProgress(
                        event.loaded /
                        event.total
                    );
                }
            };

            xhr.onload = () => {
                let data: unknown = null;

                const type =
                    xhr.getResponseHeader(
                        'content-type'
                    ) || '';

                try {
                    data = type.includes(
                        'application/json'
                    )
                        ? JSON.parse(
                            xhr.responseText
                        )
                        : xhr.responseText;
                } catch {
                    data = xhr.responseText;
                }

                if (
                    xhr.status >= 200 &&
                    xhr.status < 300
                ) {
                    resolve(
                        data as Message
                    );
                } else {
                    const error =
                        new Error(
                            `HTTP ${xhr.status}`
                        ) as Error & {
                            status: number;
                            data: unknown;
                        };

                    error.status =
                        xhr.status;
                    error.data = data;

                    reject(error);
                }
            };

            xhr.onerror = () =>
                reject(
                    new Error(
                        'Network error'
                    )
                );

            xhr.onabort = () =>
                reject(
                    new DOMException(
                        'Upload cancelled',
                        'AbortError'
                    )
                );

            xhr.send(formData);
        }
    );
}
