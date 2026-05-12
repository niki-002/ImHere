import { escapeHtml } from "./utils.js";

let toastTimer = null;

// 画面右下の短い通知を表示します。
// 連続で呼ばれた場合は前のタイマーを捨て、最新の通知だけを残します。
export function showToast(message) {
  const toastRegion = document.getElementById("toast-region");
  if (!toastRegion) return;

  toastRegion.innerHTML = `<div class="toast">${escapeHtml(message)}</div>`;

  if (toastTimer) {
    window.clearTimeout(toastTimer);
  }

  toastTimer = window.setTimeout(() => {
    toastRegion.innerHTML = "";
    toastTimer = null;
  }, 2400);
}
