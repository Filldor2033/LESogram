import { t } from "../i18n/i18n.js";
import { state } from "../state.js";

export function renderUsersList(users) {
    const list = document.getElementById("usersList");

    if (!list) return;

    list.innerHTML = "";

    if (!users.length) {
        const empty = document.createElement("div");
        empty.className = "users-empty";
        empty.textContent = t("noOnlineUsers");

        list.appendChild(empty);
        return;
    }

    for (const user of users) {
        const username = typeof user === "string" ? user : user.username;
        const isAdmin = typeof user === "object" && Boolean(user.is_admin);

        const item = document.createElement("div");
        item.className = "user-item";

        const avatar = document.createElement("div");
        avatar.className = "user-avatar";
        avatar.textContent = username.slice(0, 1).toUpperCase();

        const name = document.createElement("div");
        name.className = "user-name";
        name.textContent = username;

        const badges = document.createElement("div");
        badges.className = "user-badges";

        if (isAdmin) {
            const adminBadge = document.createElement("div");
            adminBadge.className = "user-admin-badge";
            adminBadge.textContent = `👑 ${t("adminBadge")}`;

            badges.appendChild(adminBadge);
        }

        const statusBadge = document.createElement("div");
        statusBadge.className = "user-badge";
        statusBadge.textContent = username === state.currentUser
            ? t("youBadge")
            : t("onlineBadge");

        badges.appendChild(statusBadge);

        item.appendChild(avatar);
        item.appendChild(name);
        item.appendChild(badges);

        list.appendChild(item);
    }
}

export function closeUsersPopup() {
    const popup = document.getElementById("usersPopup");

    if (popup) {
        popup.classList.add("hidden");
    }
}