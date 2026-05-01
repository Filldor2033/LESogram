export function getCurrentMentionQuery(input) {
    const value = input.value;
    const cursor = input.selectionStart ?? value.length;
    const beforeCursor = value.slice(0, cursor);

    const match = beforeCursor.match(/(^|\s)@([A-Za-z0-9_а-яА-ЯёЁ-]{0,32})$/);

    if (!match) return null;

    return {
        query: match[2].toLowerCase(),
        start: cursor - match[2].length - 1,
        end: cursor,
    };
}

export function closeMentionDropdown() {
    const dropdown = document.getElementById("mentionDropdown");

    if (!dropdown) return;

    dropdown.classList.add("hidden");
    dropdown.innerHTML = "";
}

export function getVisibleMentionOptions() {
    return Array
        .from(document.querySelectorAll("#mentionDropdown .mention-option"))
        .map(node => node.textContent.replace(/^@/, ""));
}

export function renderMentionDropdownList(users, activeIndex, onSelect) {
    const dropdown = document.getElementById("mentionDropdown");

    if (!dropdown) {
        return;
    }

    dropdown.innerHTML = "";

    users.forEach((username, index) => {
        const item = document.createElement("div");

        item.className = "mention-option" + (index === activeIndex ? " active" : "");
        item.textContent = `@${username}`;

        item.addEventListener("mousedown", (event) => {
            event.preventDefault();
            onSelect(username);
        });

        dropdown.appendChild(item);
    });

    dropdown.classList.remove("hidden");
}