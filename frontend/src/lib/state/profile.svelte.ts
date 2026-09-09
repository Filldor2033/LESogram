import {
    getMyProfile,
    updateMyProfile
} from '$lib/api/profile';

import { authState } from '$lib/state/auth.svelte';

/**
 * Self-profile state (the "personal cabinet" data).
 * Shared with the chat: display_name / avatar_url are included in
 * every message payload, so keeping them here lets the composer and
 * message list react instantly after an edit.
 */
class ProfileState {
    displayName = $state<string | null>(null);
    bio = $state<string | null>(null);
    avatarUrl = $state<string | null>(null);
    createdAt = $state<string | null>(null);

    loaded = $state(false);

    /** Modal for editing your own profile. */
    open = $state(false);

    /** Public profile card: username being viewed (null = closed). */
    viewing = $state<string | null>(null);

    async refresh(): Promise<void> {
        if (!authState.token) return;

        try {
            const profile = await getMyProfile(
                authState.token
            );

            this.displayName = profile.display_name ?? null;
            this.bio = profile.bio ?? null;
            this.avatarUrl = profile.avatar_url ?? null;
            this.createdAt = profile.created_at ?? null;
            this.loaded = true;
        } catch {
            // profile is non-critical — keep previous values
        }
    }

    async save(
        displayName: string,
        bio: string
    ): Promise<void> {
        const updated = await updateMyProfile(
            authState.token,
            {
                display_name: displayName.trim() || null,
                bio: bio.trim() || null
            }
        );

        this.displayName = updated.display_name ?? null;
        this.bio = updated.bio ?? null;
        this.avatarUrl = updated.avatar_url ?? null;
    }

    setAvatar(url: string | null): void {
        this.avatarUrl = url;
    }
}

export const profileState = new ProfileState();
