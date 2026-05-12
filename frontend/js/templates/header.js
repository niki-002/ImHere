// 上部ヘッダー、招待ポップオーバー、ユーザーメニューを組み立てます。
import { icons } from "../icons.js";
import { state } from "../state.js";
import { escapeHtml, initialFrom, userInitial } from "../utils.js";

// グループが選択されていない場合は空ヘッダーへフォールバックします。
export function headerTemplate(group) {
  if (!group) return emptyHeaderTemplate();

  return `
    <header class="topbar">
      <div class="group-heading">
        <span class="group-icon ${escapeHtml(group.color || "bg-zinc-50")}">${escapeHtml(group.emoji || "👥")}</span>
        <div>
          <h1>${escapeHtml(group.name)}</h1>
          <p>メンバー ${group.members.length}人</p>
        </div>
      </div>
      ${userActionsTemplate(group)}
    </header>
  `;
}

// グループが1件もない時のヘッダーです。
function emptyHeaderTemplate() {
  return `
    <header class="topbar">
      <div class="group-heading">
        <span class="group-icon">👥</span>
        <div>
          <h1>グループ未選択</h1>
          <p>メンバー 0人</p>
        </div>
      </div>
      ${userActionsTemplate(null)}
    </header>
  `;
}

// 右側の招待ボタン、ユーザーアバター、メニューをまとめます。
function userActionsTemplate(group) {
  return `
    <div class="topbar-actions">
      ${group ? inviteButtonTemplate() : ""}
      <button class="user-avatar-button" type="button" data-action="toggle-user-menu" aria-label="ユーザーメニュー">
        ${escapeHtml(userInitial(state))}
      </button>
      ${state.userMenuOpen ? userMenuTemplate() : ""}
    </div>
  `;
}

// グループ選択時だけ招待ボタンを表示します。
function inviteButtonTemplate() {
  return `
    <button class="button button-muted" type="button" data-action="toggle-invite">
      ${icons.add}
      <span class="optional-label">招待</span>
    </button>
    ${state.inviteOpen ? invitePopoverTemplate() : ""}
  `;
}

// ユーザー名検索、候補選択、招待実行を行うポップオーバーです。
function invitePopoverTemplate() {
  return `
    <div class="popover" data-popover-root>
      <div class="invite-form">
        <div class="invite-search-row">
          <label class="search-field">
            <span class="sr-only">ユーザー名</span>
            <input class="input" type="text" data-field="invite-query" value="${escapeHtml(state.inviteQuery)}" placeholder="ユーザー名を入力" autocomplete="off">
            ${state.searchingUsers ? '<span class="searching-label">検索中...</span>' : ""}
          </label>
          <button class="button button-primary" type="button" data-action="invite-user" ${state.inviting || !state.inviteQuery.trim() ? "disabled" : ""}>
            ${state.inviting ? '<span class="spinner" aria-hidden="true"></span>' : ""}
            <span>招待</span>
          </button>
          <button class="icon-button" type="button" data-action="close-invite" aria-label="閉じる">${icons.close}</button>
        </div>

        ${state.selectedCandidate ? selectedCandidateTemplate(state.selectedCandidate) : ""}
        ${!state.selectedCandidate && state.inviteCandidates.length ? `<ul class="candidate-list">${state.inviteCandidates.map(candidateTemplate).join("")}</ul>` : ""}
        ${!state.searchingUsers && state.inviteQuery.trim() && !state.inviteCandidates.length && !state.selectedCandidate ? '<p class="hint">ユーザーが見つかりません</p>' : ""}
      </div>
    </div>
  `;
}

// 検索候補を選択済みにした時の表示です。
function selectedCandidateTemplate(user) {
  return `
    <div class="selected-user">
      <span class="avatar bg-blue-100 text-blue-800">${escapeHtml(initialFrom(user.name || user.username))}</span>
      <span>${escapeHtml(user.name || user.displayName || user.username)}</span>
      <button class="icon-button" type="button" data-action="clear-selected-candidate" aria-label="選択解除">${icons.close}</button>
    </div>
  `;
}

// 検索結果1件分のボタンです。
function candidateTemplate(user) {
  return `
    <li>
      <button class="candidate-button" type="button" data-action="select-candidate" data-user-id="${user.id}">
        <span class="avatar bg-zinc-100 text-zinc-800">${escapeHtml(initialFrom(user.name || user.username))}</span>
        <span>
          <span class="candidate-name">${escapeHtml(user.name || user.displayName || user.username)}</span>
          <span class="candidate-meta">@${escapeHtml(user.username)}</span>
        </span>
      </button>
    </li>
  `;
}

// ユーザーアバターから開くメニューです。
function userMenuTemplate() {
  return `
    <div class="popover menu" data-popover-root>
      <button class="menu-button" type="button" data-action="refresh-data">${icons.search}<span>再読み込み</span></button>
      <button class="menu-button" type="button" data-action="show-api-base">${icons.settings}<span>API URL</span></button>
      <button class="menu-button danger" type="button" data-action="logout">${icons.logout}<span>ログアウト</span></button>
    </div>
  `;
}
