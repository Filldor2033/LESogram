export interface MentionQuery {
    query: string;
    start: number;
    end: number;
}

export function getMentionQuery(
    value: string,
    cursor: number
): MentionQuery | null {
    const beforeCursor =
        value.slice(0, cursor);

    const match =
        beforeCursor.match(
            /(^|\s)@([A-Za-z0-9_а-яА-ЯёЁ-]{0,32})$/
        );

    if (!match) {
        return null;
    }

    return {
        query:
            match[2].toLowerCase(),

        start:
            cursor -
            match[2].length -
            1,

        end: cursor
    };
}