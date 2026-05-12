// メンバー一覧とメンバーカードを組み立てるテンプレートです。
import { icons } from "../icons.js";
import { state } from "../state.js";
import { escapeHtml, initialFrom, statusMeta } from "../utils.js";

// 選択中グループのメンバー一覧エリアです。
export function membersTemplate(group) {
  return `
    <section class="content" aria-label="メンバーのステータス">
      <p class="section-label">メンバーのステータス</p>
      ${state.pageError ? `<div class="error-box" role="alert">${icons.alert}<span>${escapeHtml(state.pageError)}</span></div>` : ""}
      ${state.loadingGroups ? emptySmallTemplate("読み込み中...") : membersBodyTemplate(group)}
    </section>
  `;
}

// グループがまだない場合のメインエリアです。
export function noGroupsTemplate() {
  return `
    <section class="content">
      <div class="empty-state">
        ${icons.group}
        <h2>グループを作成</h2>
        <p>グループはまだありません</p>
        <button class="button button-primary" type="button" data-action="open-group-modal">
          ${icons.add}
          <span>グループを追加</span>
        </button>
      </div>
    </section>
  `;
}

// 読み込み中、空、一覧ありの表示を切り替えます。
function membersBodyTemplate(group) {
  if (!group.members.length) {
    return `
      <div class="empty-state">
        ${icons.group}
        <h2>まだメンバーがいません</h2>
        <p>メンバーはまだ追加されていません</p>
      </div>
    `;
  }

  return `
    <div class="members-grid">
      ${group.members.map((member) => memberCardTemplate(group, member)).join("")}
    </div>
  `;
}

// メンバー1人分のカードです。
function memberCardTemplate(group, member) {
  const isSelf = member.userId === state.user?.id || member.username === state.user?.username;
  const canRemove = group.ownerId === state.user?.id && !isSelf;
  const status = statusMeta(member.status);

  return `
    <article class="member-card">
      <div class="member-top">
        <span class="avatar ${escapeHtml(member.avatarBg)} ${escapeHtml(member.avatarText)}">${escapeHtml(member.initial || initialFrom(member.name || member.username))}</span>
        <div class="member-name">
          <strong>${escapeHtml(member.name || member.displayName || member.username)}</strong>
          <span>${escapeHtml(member.time || "今")}</span>
        </div>
        ${canRemove ? removeMemberButtonTemplate(group.id, member.username) : memberRoleTemplate(isSelf, member.role)}
      </div>
      <div class="status-badge status-${escapeHtml(member.status || status.type)}">
        <span class="status-dot"></span>
        <span>${escapeHtml(member.statusEmoji || status.emoji)}</span>
        <span>${escapeHtml(member.statusLabel || status.label)}</span>
      </div>
    </article>
  `;
}

// オーナーだけが表示できるメンバー削除ボタンです。
function removeMemberButtonTemplate(groupId, username) {
  return `
    <button class="icon-button" type="button" data-action="remove-member" data-group-id="${groupId}" data-username="${escapeHtml(username)}" aria-label="メンバー削除">
      ${icons.close}
    </button>
  `;
}

// 自分または管理者であることを小さく表示します。
function memberRoleTemplate(isSelf, role) {
  return `<span class="self-pill">${isSelf ? "自分" : escapeHtml(role === "owner" ? "管理" : "")}</span>`;
}

// ローディングや空状態などの短いプレースホルダーです。
function emptySmallTemplate(message) {
  return `
    <div class="empty-state">
      ${icons.group}
      <p>${escapeHtml(message)}</p>
    </div>
  `;
}
