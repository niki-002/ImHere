import { STATUS_OPTIONS } from "./constants.js";

// テンプレート文字列へユーザー入力を埋め込む前にエスケープします。
export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// 空レスポンスや不正JSONでも落ちないJSONパーサーです。
export function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// ステータス値から表示ラベル・絵文字を取得します。
export function statusMeta(type) {
  return STATUS_OPTIONS.find((item) => item.type === type) || STATUS_OPTIONS[0];
}

// アバターに表示する1文字を作ります。
export function initialFrom(value) {
  return String(value || "?").trim().slice(0, 1) || "?";
}

// ログインユーザーの表示名からヘッダー用の頭文字を作ります。
export function userInitial(appState) {
  return initialFrom(
    appState.user?.displayName ||
      appState.user?.name ||
      appState.user?.username ||
      "U",
  ).toUpperCase();
}

// バックエンドのcamelCase/snake_case差をここで吸収します。
export function normalizeGroups(groups) {
  return (Array.isArray(groups) ? groups : []).map((group) => ({
    ...group,
    ownerId: group.ownerId ?? group.owner_id,
    members: normalizeMembers(group.members),
  }));
}

// メンバー情報をテンプレートが扱いやすい形に揃えます。
export function normalizeMembers(members) {
  return (Array.isArray(members) ? members : []).map((member) => ({
    ...member,
    userId: member.userId ?? member.user_id,
    displayName: member.displayName ?? member.display_name ?? member.name,
    avatarBg: member.avatarBg ?? member.avatar_bg ?? "bg-zinc-100",
    avatarText: member.avatarText ?? member.avatar_text ?? "text-zinc-800",
    statusLabel: member.statusLabel ?? member.status_label ?? statusMeta(member.status).label,
    statusEmoji: member.statusEmoji ?? member.status_emoji ?? statusMeta(member.status).emoji,
    updatedAt: member.updatedAt ?? member.updated_at,
    initial: member.initial ?? member.initials ?? initialFrom(member.name || member.username),
    time: member.time || "今",
  }));
}

// 選択中グループが消えた場合は先頭グループを使います。
export function getActiveGroup(appState) {
  return (
    appState.groups.find((group) => group.id === appState.activeGroupId) ||
    appState.groups[0] ||
    null
  );
}

// 削除や再取得でactiveGroupIdが無効になった時に補正します。
export function reconcileActiveGroup(appState) {
  const hasActive = appState.groups.some((group) => group.id === appState.activeGroupId);
  appState.activeGroupId = hasActive ? appState.activeGroupId : appState.groups[0]?.id ?? null;
}

// 自分のステータス更新後、グループ内の自分カードも即時更新します。
export function updateCurrentUserInGroups(appState, statusResponse) {
  if (!appState.user || !statusResponse) return;

  appState.groups = appState.groups.map((group) => ({
    ...group,
    members: group.members.map((member) => {
      const isCurrentUser =
        member.userId === appState.user.id || member.username === appState.user.username;
      if (!isCurrentUser) return member;

      return {
        ...member,
        status: statusResponse.status,
        statusLabel: statusResponse.statusLabel,
        statusEmoji: statusResponse.statusEmoji,
        time: statusResponse.time,
        updatedAt: statusResponse.updatedAt,
      };
    }),
  }));
}
