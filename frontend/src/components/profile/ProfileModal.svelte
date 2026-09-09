<script lang="ts">
        import { fade, scale } from 'svelte/transition';

    import Avatar from '$components/common/Avatar.svelte';
    import Icon from '$components/common/Icon.svelte';

    import {
        authState
    } from '$lib/state/auth.svelte';
    import {
        profileState
    } from '$lib/state/profile.svelte';

    import {
        changeMyPassword,
        deleteAvatar,
        getAdminRooms,
        getAdminUsers,
        getMyStats,
        setAdminRole,
        uploadAvatar
    } from '$lib/api/profile';

    import {
        getApiErrorMessage
    } from '$lib/i18n/api-errors';
    import { t } from '$lib/i18n/i18n.svelte';

    import type {
        TranslationKey
    } from '$lib/i18n/translations';

    import type {
        AdminRoom,
        AdminUser,
        UserStats
    } from '$lib/types/auth';

    let tab = $state<'profile' | 'security' | 'stats' | 'admin'>(
        'profile'
    );

    let name = $state('');
    let bio = $state('');
    let saving = $state(false);
    let savedAt = $state(0);
    let error = $state<string | null>(null);

    let avatarError = $state<string | null>(null);
    let uploading = $state(false);
    let fileInput = $state<HTMLInputElement>();

    // password form
    let currentPassword = $state('');
    let newPassword = $state('');
    let passwordError = $state<string | null>(null);
    let passwordOk = $state(false);
    let changingPassword = $state(false);

    // stats
    let stats = $state<UserStats | null>(null);
    let statsLoading = $state(false);

    // admin
    let adminUsers = $state<AdminUser[]>([]);
    let adminRooms = $state<AdminRoom[]>([]);
    let adminLoading = $state(false);
    let roleSaving = $state<string | null>(null);

    const AVATAR_MAX_BYTES = 5 * 1024 * 1024;

    // sync form fields when the modal opens
    $effect(() => {
        if (profileState.open) {
            name = profileState.displayName ?? '';
            bio = profileState.bio ?? '';
            error = null;
            avatarError = null;
            savedAt = 0;
            currentPassword = '';
            newPassword = '';
            passwordError = null;
            passwordOk = false;
            stats = null;
            adminUsers = [];
            adminRooms = [];
            tab = 'profile';
        }
    });

    async function saveProfile() {
        if (saving) return;

        saving = true;
        error = null;

        try {
            await profileState.save(name, bio);
            savedAt = Date.now();
        } catch (e) {
            error = getApiErrorMessage(e, 'profileSaveFailed');
        } finally {
            saving = false;
        }
    }

    async function onAvatarSelected(e: Event) {
        const input = e.target as HTMLInputElement;
        const file = input.files?.[0];
        input.value = '';

        if (!file) return;

        avatarError = null;

        if (file.size > AVATAR_MAX_BYTES) {
            avatarError = t('avatarTooLarge');
            return;
        }

        uploading = true;

        try {
            const res = await uploadAvatar(
                authState.token,
                file
            );
            profileState.setAvatar(res.avatar_url);
        } catch (e) {
            avatarError = getApiErrorMessage(e, 'avatarUploadFailed');
        } finally {
            uploading = false;
        }
    }

    async function removeAvatar() {
        avatarError = null;

        try {
            await deleteAvatar(authState.token);
            profileState.setAvatar(null);
        } catch (e) {
            avatarError = getApiErrorMessage(e, 'avatarUploadFailed');
        }
    }

    async function submitPassword() {
        if (changingPassword) return;

        passwordError = null;
        passwordOk = false;

        if (newPassword.length < 4) {
            passwordError = t('passwordTooShort');
            return;
        }

        changingPassword = true;

        try {
            await changeMyPassword(authState.token, {
                current_password: currentPassword,
                new_password: newPassword
            });

            passwordOk = true;
            currentPassword = '';
            newPassword = '';
        } catch (e) {
            passwordError = getApiErrorMessage(e, 'passwordChangeFailed');
        } finally {
            changingPassword = false;
        }
    }

    async function loadStats() {
        if (statsLoading || stats) return;

        statsLoading = true;

        try {
            stats = await getMyStats(authState.token);
        } finally {
            statsLoading = false;
        }
    }

    async function loadAdmin() {
        if (adminLoading || adminUsers.length) return;

        adminLoading = true;

        try {
            const [u, r] = await Promise.all([
                getAdminUsers(authState.token),
                getAdminRooms(authState.token)
            ]);

            adminUsers = u.users;
            adminRooms = r.rooms;
        } finally {
            adminLoading = false;
        }
    }

    function switchTab(next: 'profile' | 'security' | 'stats' | 'admin') {
        tab = next;

        if (next === 'stats') void loadStats();
        if (next === 'admin') void loadAdmin();
    }

    async function toggleRole(user: AdminUser) {
        if (roleSaving) return;

        roleSaving = user.username;

        try {
            await setAdminRole(
                authState.token,
                user.username,
                !user.is_admin
            );

            adminUsers = adminUsers.map((u) =>
                u.username === user.username
                    ? { ...u, is_admin: !u.is_admin }
                    : u
            );
        } catch (e) {
            avatarError = getApiErrorMessage(e, 'adminActionFailed');
        } finally {
            roleSaving = null;
        }
    }

    function formatDate(iso?: string | null): string {
        if (!iso) return '—';

        try {
            return new Date(iso).toLocaleDateString();
        } catch {
            return '—';
        }
    }

    const savedRecently = $derived(
        savedAt > 0 && Date.now() - savedAt < 2500
    );

    const typeLabels: Record<string, TranslationKey> = {
        text: 'profileStatText',
        image: 'profileStatImages',
        gif: 'profileStatImages',
        video: 'profileStatVideos',
        voice: 'profileStatVoice',
        file: 'profileStatFiles'
    };
</script>

{#if profileState.open}
    <div
        class="modal-overlay"
        transition:fade={{ duration: 140 }}
        onclick={() => (profileState.open = false)}
        role="presentation"
    >
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
        <!-- svelte-ignore a11y_interactive_supports_focus -->
        <div
            class="modal profile-modal"
            transition:scale={{ duration: 160, start: 0.96 }}
            onclick={(e) => e.stopPropagation()}
            role="dialog"
            aria-label={t('profileTitle')}
        >
            <div class="profile-head">
                <Avatar
                    username={authState.username}
                    displayName={profileState.displayName}
                    url={profileState.avatarUrl}
                    size={52}
                />

                <div class="profile-head-info">
                    <div class="profile-head-name">
                        {profileState.displayName ||
                            authState.username}
                    </div>

                    <div class="profile-head-sub">
                        @{authState.username}
                        {#if authState.isAdmin}
                            <span class="admin-chip">
                                {t('adminBadge')}
                            </span>
                        {/if}
                    </div>

                    {#if profileState.createdAt}
                        <div class="profile-head-date">
                            {t('profileRegistered')}:
                            {formatDate(profileState.createdAt)}
                        </div>
                    {/if}
                </div>

                <button
                    class="profile-close"
                    type="button"
                    aria-label={t('close')}
                    onclick={() => (profileState.open = false)}
                >
                    ×
                </button>
            </div>

            <div class="profile-tabs">
                <button
                    class="profile-tab"
                    class:active={tab === 'profile'}
                    type="button"
                    onclick={() => switchTab('profile')}
                >
                    {t('profileTabProfile')}
                </button>

                <button
                    class="profile-tab"
                    class:active={tab === 'security'}
                    type="button"
                    onclick={() => switchTab('security')}
                >
                    {t('profileTabSecurity')}
                </button>

                <button
                    class="profile-tab"
                    class:active={tab === 'stats'}
                    type="button"
                    onclick={() => switchTab('stats')}
                >
                    {t('profileTabStats')}
                </button>

                {#if authState.isAdmin}
                    <button
                        class="profile-tab"
                        class:active={tab === 'admin'}
                        type="button"
                        onclick={() => switchTab('admin')}
                    >
                        {t('profileTabAdmin')}
                    </button>
                {/if}
            </div>

            <div class="profile-body">
                {#if tab === 'profile'}
                    <div class="profile-form">
                        <label class="field">
                            <span class="field-label">
                                {t('profileDisplayName')}
                            </span>

                            <input
                                type="text"
                                bind:value={name}
                                maxlength="50"
                                placeholder={authState.username}
                            />
                        </label>

                        <label class="field">
                            <span class="field-label">
                                {t('profileBio')}
                            </span>

                            <textarea
                                bind:value={bio}
                                maxlength="200"
                                rows="3"
                                placeholder={t('profileBioPlaceholder')}
                            ></textarea>
                        </label>

                        <div class="avatar-row">
                            <div class="avatar-controls">
                                <button
                                    class="secondary"
                                    type="button"
                                    disabled={uploading}
                                    onclick={() =>
                                        fileInput?.click()}
                                >
                                    {uploading
                                        ? t('loading')
                                        : t('avatarUpload')}
                                </button>

                                {#if profileState.avatarUrl}
                                    <button
                                        class="secondary danger"
                                        type="button"
                                        onclick={removeAvatar}
                                    >
                                        {t('avatarRemove')}
                                    </button>
                                {/if}

                                <input
                                    type="file"
                                    accept="image/png,image/jpeg,image/webp,image/gif"
                                    hidden
                                    bind:this={fileInput}
                                    onchange={onAvatarSelected}
                                />
                            </div>

                            <span class="field-hint">
                                {t('avatarHint')}
                            </span>
                        </div>

                        {#if avatarError}
                            <div class="form-error">
                                {avatarError}
                            </div>
                        {/if}

                        {#if error}
                            <div class="form-error">
                                {error}
                            </div>
                        {/if}

                        <div class="profile-actions">
                            <button
                                type="button"
                                disabled={saving}
                                onclick={saveProfile}
                            >
                                {saving
                                    ? t('loading')
                                    : t('save')}
                            </button>

                            {#if savedRecently}
                                <span class="saved-note">
                                    ✓ {t('saved')}
                                </span>
                            {/if}
                        </div>
                    </div>

                {:else if tab === 'security'}
                    <form
                        class="profile-form"
                        onsubmit={(e) => {
                            e.preventDefault();
                            void submitPassword();
                        }}
                    >
                        <label class="field">
                            <span class="field-label">
                                {t('profileCurrentPassword')}
                            </span>

                            <input
                                type="password"
                                bind:value={currentPassword}
                                autocomplete="current-password"
                            />
                        </label>

                        <label class="field">
                            <span class="field-label">
                                {t('profileNewPassword')}
                            </span>

                            <input
                                type="password"
                                bind:value={newPassword}
                                autocomplete="new-password"
                            />
                        </label>

                        {#if passwordError}
                            <div class="form-error">
                                {passwordError}
                            </div>
                        {/if}

                        {#if passwordOk}
                            <div class="form-ok">
                                ✓ {t('passwordChanged')}
                            </div>
                        {/if}

                        <div class="profile-actions">
                            <button
                                type="submit"
                                disabled={changingPassword}
                            >
                                {changingPassword
                                    ? t('loading')
                                    : t('profileChangePassword')}
                            </button>
                        </div>
                    </form>

                {:else if tab === 'stats'}
                    {#if statsLoading}
                        <div class="profile-empty">
                            {t('loading')}
                        </div>
                    {:else if stats}
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-value">
                                    {stats.total_messages}
                                </div>
                                <div class="stat-label">
                                    {t('profileStatTotal')}
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-value">
                                    {stats.recent_messages}
                                </div>
                                <div class="stat-label">
                                    {t('profileStatRecent')}
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-value">
                                    {stats.rooms_active_in}
                                </div>
                                <div class="stat-label">
                                    {t('profileStatRooms')}
                                </div>
                            </div>

                            <div class="stat-card">
                                <div class="stat-value">
                                    {formatDate(
                                        stats.first_message_at
                                    )}
                                </div>
                                <div class="stat-label">
                                    {t('profileStatFirst')}
                                </div>
                            </div>
                        </div>

                        <div class="stats-breakdown">
                            {#each Object.entries(
                                stats.messages_by_type
                            ) as [type, count]}
                                <div class="stat-row">
                                    <span>
                                        {t(
                                            typeLabels[type] ??
                                                'profileStatFiles'
                                        )}
                                    </span>
                                    <b>{count}</b>
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <div class="profile-empty">
                            {t('profileNoStats')}
                        </div>
                    {/if}

                {:else if tab === 'admin' && authState.isAdmin}
                    {#if adminLoading}
                        <div class="profile-empty">
                            {t('loading')}
                        </div>
                    {:else}
                        <div class="admin-section">
                            <h4>{t('adminUsersTitle')}</h4>

                            <div class="admin-list">
                                {#each adminUsers as user (user.username)}
                                    <div class="admin-row">
                                        <Avatar
                                            username={user.username}
                                            displayName={
                                                user.display_name
                                            }
                                            url={user.avatar_url}
                                            size={26}
                                        />

                                        <span class="admin-name">
                                            {user.display_name ||
                                                user.username}
                                        </span>

                                        <span class="admin-sub">
                                            @{user.username}
                                            · {user.message_count}
                                            {t('profileStatTotal')}
                                        </span>

                                        <button
                                            class="secondary role-btn"
                                            type="button"
                                            disabled={roleSaving ===
                                                user.username}
                                            onclick={() =>
                                                void toggleRole(user)}
                                        >
                                            {user.is_admin
                                                ? t('adminRevoke')
                                                : t('adminGrant')}
                                        </button>
                                    </div>
                                {/each}
                            </div>
                        </div>

                        <div class="admin-section">
                            <h4>{t('adminRoomsTitle')}</h4>

                            <div class="admin-list">
                                {#each adminRooms as room (room.name)}
                                    <div class="admin-row">
                                        <span class="admin-name">
                                            {room.name}
                                        </span>

                                        <span class="admin-sub">
                                            {t('adminCreatedBy')}
                                            @{room.created_by}
                                            · {room.message_count}
                                            {t('profileStatTotal')}
                                        </span>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    {/if}
                {/if}
            </div>
        </div>
    </div>
{/if}
