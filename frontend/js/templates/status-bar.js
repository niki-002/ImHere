// 自分のステータスを切り替える横スクロールバーです。
import { STATUS_OPTIONS } from "../constants.js";
import { state } from "../state.js";
import { escapeHtml } from "../utils.js";

// STATUS_OPTIONSの定義をそのままチップ一覧として描画します。
export function statusBarTemplate() {
  return `
    <section class="status-bar" aria-label="自分のステータス">
      <p class="section-label">自分のステータス</p>
      <div class="status-scroll">
        ${STATUS_OPTIONS.map(statusChipTemplate).join("")}
      </div>
    </section>
  `;
}

// 現在のステータスと一致するチップにis-activeを付けます。
function statusChipTemplate(status) {
  return `
    <button class="status-chip ${state.currentStatus === status.type ? "is-active" : ""}" type="button" data-action="set-status" data-status="${status.type}">
      <span>${status.emoji}</span>
      <span>${escapeHtml(status.label)}</span>
    </button>
  `;
}
