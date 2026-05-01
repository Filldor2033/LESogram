import { loadRoomUsersRequest } from "../api/rooms-api.js";
import { state } from "../state.js";

import {
    closeMentionDropdown as closeMentionDropdownUi,
    getCurrentMentionQuery,
    getVisibleMentionOptions as getVisibleMentionOptionsUi,
    renderMentionDropdownList,
} from "../ui/mentions-ui.js";

export async function refreshMentionUsers() {
    if (!state.currentRoom || !state.currentRoomToken) {
        state.mentionUsers = [];
        return;
    }

    const { res, data } = await loadRoomUsersRequest(
        state.currentRoom,
        state.currentRoomToken
    );

    if (!res.ok) {
        state.mentionUsers = [];
        return;
    }

    setMentionUsers(data);
}

export function setMentionUsers(data) {
    state.mentionUsers = (data.users || [])
        .map(user => typeof user === "string" ? user : user.username)
        .filter(username => username && username !== state.currentUser);
}

export function renderMentionDropdown() {
    const input = document.getElementById("message");
    const mention = input ? getCurrentMentionQuery(input) : null;

    if (!mention) {
        closeMentionDropdown();
        return;
    }

    const users = state.mentionUsers
        .filter(username => username.toLowerCase().includes(mention.query))
        .slice(0, 8);

    if (!users.length) {
        closeMentionDropdown();
        return;
    }

    state.mentionDropdownIndex = Math.min(
        state.mentionDropdownIndex,
        users.length - 1
    );

    renderMentionDropdownList(
        users,
        state.mentionDropdownIndex,
        insertMention
    );
}

export function insertMention(username) {
    const input = document.getElementById("message");

    if (!input) return;

    const mention = getCurrentMentionQuery(input);

    if (!mention) return;

    const before = input.value.slice(0, mention.start);
    const after = input.value.slice(mention.end);

    input.value = `${before}@${username} ${after}`;

    const cursor = before.length + username.length + 2;

    input.focus();
    input.setSelectionRange(cursor, cursor);

    closeMentionDropdown();
}

export function closeMentionDropdown() {
    closeMentionDropdownUi();
}

export function getVisibleMentionOptions() {
    return getVisibleMentionOptionsUi();
}