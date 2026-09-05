import {
    translations,
    type Language,
    type TranslationKey,
    type TranslationVars
} from './translations';

const LANGUAGE_KEY = 'language';

function isLanguage(
    value: unknown
): value is Language {
    return (
        value === 'en' ||
        value === 'ru'
    );
}

function getInitialLanguage(): Language {
    if (typeof window === 'undefined') {
        return 'en';
    }

    const saved =
        localStorage.getItem(LANGUAGE_KEY);

    if (isLanguage(saved)) {
        return saved;
    }

    return navigator.language
        .toLowerCase()
        .startsWith('ru')
            ? 'ru'
            : 'en';
}

class I18nState {
    language = $state<Language>(
        getInitialLanguage()
    );

    setLanguage(
        language: Language
    ): void {
        if (this.language === language) {
            return;
        }

        this.language = language;

        localStorage.setItem(
            LANGUAGE_KEY,
            language
        );

        this.syncDocumentLanguage();
    }

    syncDocumentLanguage(): void {
        if (typeof document === 'undefined') {
            return;
        }

        document.documentElement.lang =
            this.language;
    }
}

export const i18n =
    new I18nState();

export function t(
    key: TranslationKey,
    vars: TranslationVars = {}
): string {
    const source =
        translations[i18n.language][key] ??
        translations.en[key];

    return source.replace(
        /\{(\w+)\}/g,
        (_, name: string) => {
            const value = vars[name];

            return value === undefined
                ? `{${name}}`
                : String(value);
        }
    );
}

export function pluralizeRu(
    count: number,
    one: string,
    few: string,
    many: string
): string {
    const mod10 = count % 10;
    const mod100 = count % 100;

    if (
        mod10 === 1 &&
        mod100 !== 11
    ) {
        return one;
    }

    if (
        mod10 >= 2 &&
        mod10 <= 4 &&
        (
            mod100 < 12 ||
            mod100 > 14
        )
    ) {
        return few;
    }

    return many;
}

export function formatUserCount(
    count: number
): string {
    if (i18n.language === 'ru') {
        return pluralizeRu(
            count,
            t('userCount_one', { count }),
            t('userCount_few', { count }),
            t('userCount_many', { count })
        );
    }

    return count === 1
        ? t('userCount_one', { count })
        : t('userCount_many', { count });
}

export function formatRoomCount(
    count: number
): string {
    if (i18n.language === 'ru') {
        return pluralizeRu(
            count,
            t('roomCount_one', { count }),
            t('roomCount_few', { count }),
            t('roomCount_many', { count })
        );
    }

    return count === 1
        ? t('roomCount_one', { count })
        : t('roomCount_many', { count });
}
