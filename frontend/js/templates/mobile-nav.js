// モバイル画面下部のグループ切り替えナビです。
import { state } from "../state.js";
import { escapeHtml } from "../utils.js";

// 画面幅が狭い時は最大4グループと追加ボタンだけを表示します。
export function mobileNavTemplate() {
  return `
    <nav class="mobile-nav" aria-label="モバイルグループ">
      ${state.groups.slice(0, 4).map(mobileGroupButtonTemplate).join("")}
      <button class="mobile-nav-button" type="button" data-action="open-group-modal">
        <span>＋</span>
        <span>追加</span>
      </button>
    </nav>
  `;
}

// モバイルナビのグループボタン1つ分です。
function mobileGroupButtonTemplate(group) {
  return `
    <button class="mobile-nav-button ${group.id === state.activeGroupId ? "is-active" : ""}" type="button" data-action="select-group" data-group-id="${group.id}">
      <span>${escapeHtml(group.emoji || "👥")}</span>
      <span>${escapeHtml(group.name)}</span>
    </button>
  `;
}
