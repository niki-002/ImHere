import { state } from "./state.js";
import { appTemplate } from "./templates/app.js";
import { authTemplate, bootTemplate } from "./templates/auth.js";

const app = document.getElementById("app");

// stateの内容から画面全体を再生成します。
// 小規模SPAなので、差分更新ではなくテンプレートの再描画で揃えています。
export function render() {
  app.setAttribute("aria-busy", state.booting ? "true" : "false");

  if (state.booting) {
    app.innerHTML = bootTemplate();
  } else {
    app.innerHTML = state.user && state.token ? appTemplate() : authTemplate();
  }

  restoreFocus();
}

// 再描画で消えた入力欄へフォーカスを戻します。
// 招待検索やモーダル表示直後の操作感を保つための処理です。
function restoreFocus() {
  if (!state.focusSelector) return;

  const selector = state.focusSelector;
  state.focusSelector = "";

  window.requestAnimationFrame(() => {
    const node = document.querySelector(selector);
    if (!node) return;

    node.focus();
    if (typeof node.setSelectionRange === "function") {
      const length = node.value.length;
      node.setSelectionRange(length, length);
    }
  });
}
