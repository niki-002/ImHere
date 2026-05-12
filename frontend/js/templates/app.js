// メインアプリ画面の大枠を組み立てるテンプレートです。
import { API_BASE } from "../constants.js";
import { state } from "../state.js";
import { getActiveGroup } from "../utils.js";
import { groupModalTemplate } from "./group-modal.js";
import { headerTemplate } from "./header.js";
import { membersTemplate, noGroupsTemplate } from "./members.js";
import { mobileNavTemplate } from "./mobile-nav.js";
import { sidebarTemplate } from "./sidebar.js";
import { statusBarTemplate } from "./status-bar.js";

// サイドバー、ヘッダー、ステータス、メンバー一覧を合成します。
export function appTemplate() {
  const activeGroup = getActiveGroup(state);

  return `
    <div class="shell">
      ${sidebarTemplate(activeGroup)}
      <main class="main">
        ${headerTemplate(activeGroup)}
        ${statusBarTemplate()}
        ${activeGroup ? membersTemplate(activeGroup) : noGroupsTemplate()}
        ${mobileNavTemplate()}
      </main>
      ${state.groupModalOpen ? groupModalTemplate() : ""}
    </div>
  `;
}

// ユーザーメニューで現在の接続先APIを表示するための文言です。
export function apiBaseLabel() {
  return `API: ${API_BASE}`;
}
