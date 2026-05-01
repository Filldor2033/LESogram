import { state } from "../state.js";
import { translations } from "./translations.js";

export function getInitialLanguage() {
    const saved = localStorage.getItem("language");

    if (saved === "en" || saved === "ru") {
        return saved;
    }

    return navigator.language &&
        navigator.language.toLowerCase().startsWith("ru")
        ? "ru"
        : "en";
}

export function t(key, vars = {}) {
    const lang = state.currentLanguage || "en";
    const source = translations[lang][key] ?? translations.en[key] ?? key;

    return source.replace(/\{(\w+)\}/g, (_, name) =>
        String(vars[name] ?? `{${name}}`)
    );
}

export function pluralizeRu(count, one, few, many) {
    const mod10 = count % 10;
    const mod100 = count % 100;

    if (mod10 === 1 && mod100 !== 11) return one;

    if (
        mod10 >= 2 &&
        mod10 <= 4 &&
        (mod100 < 12 || mod100 > 14)
    ) {
        return few;
    }

    return many;
}

export function formatUserCount(count) {
    if (state.currentLanguage === "ru") {
        return pluralizeRu(
            count,
            t("userCount_one", { count }),
            t("userCount_few", { count }),
            t("userCount_many", { count })
        );
    }

    return count === 1
        ? t("userCount_one", { count })
        : t("userCount_many", { count });
}

export function formatRoomCount(count) {
    if (state.currentLanguage === "ru") {
        return pluralizeRu(
            count,
            t("roomCount_one", { count }),
            t("roomCount_few", { count }),
            t("roomCount_many", { count })
        );
    }

    return count === 1
        ? t("roomCount_one", { count })
        : t("roomCount_many", { count });
}

export function setLanguage(language, onChange) {
    if (!translations[language]) return;

    state.currentLanguage = language;
    localStorage.setItem("language", language);

    if (typeof onChange === "function") {
        onChange();
    }
}