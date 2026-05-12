// PC表示の左サイドバーを組み立てるテンプレートです。
import { icons } from "../icons.js";
import { state } from "../state.js";
import { escapeHtml } from "../utils.js";

// グループ一覧とグループ追加ボタンを表示します。
export function sidebarTemplate(activeGroup) {
  return `
    <aside class="sidebar" aria-label="グループ">
      <div class="sidebar-logo">
        <div class="brand-mark" aria-hidden="true">${icons.info}</div>
        <span>imhere</span>
      </div>
      <div class="sidebar-scroll">
        <p class="section-label">グループ</p>
        <div class="group-list">
          ${state.groups.length ? state.groups.map((group) => groupRowTemplate(group, activeGroup?.id)).join("") : emptyGroupListTemplate()}
        </div>
      </div>
      <div class="sidebar-footer">
        <button class="button button-muted button-full" type="button" data-action="open-group-modal">
          ${icons.add}
          <span>グループを追加</span>
        </button>
      </div>
    </aside>
  `;
}

// 1グループ分の行です。権限に応じて削除/退会アイコンを切り替えます。
function groupRowTemplate(group, activeId) {
  const isActive = group.id === activeId;
  const canDelete = group.ownerId === state.user?.id;

  return `
    <div class="group-row ${isActive ? "is-active" : ""}">
      <button class="group-main" type="button" data-action="select-group" data-group-id="${group.id}">
        <span class="group-icon ${escapeHtml(group.color || "bg-zinc-50")}">${escapeHtml(group.emoji || "👥")}</span>
        <span class="group-name">${escapeHtml(group.name)}</span>
        <span class="count-pill">${group.members.length}</span>
      </button>
      <button class="icon-button" type="button" data-action="${canDelete ? "delete-group" : "leave-group"}" data-group-id="${group.id}" title="${canDelete ? "グループ削除" : "グループ退会"}" aria-label="${canDelete ? "グループ削除" : "グループ退会"}">
        ${canDelete ? icons.trash : icons.logout}
      </button>
    </div>
  `;
}

// グループ未作成時のサイドバー内表示です。
function emptyGroupListTemplate() {
  return `
    <div class="empty-state">
      ${icons.group}
      <p>まだグループがありません</p>
    </div>
  `;
}
