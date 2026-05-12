// ログイン/新規登録画面を組み立てるテンプレートです。
import { icons } from "../icons.js";
import { state } from "../state.js";
import { escapeHtml } from "../utils.js";

// 起動直後、セッション復元中に表示する簡易画面です。
export function bootTemplate() {
  return `
    <div class="boot-screen">
      <div class="brand-mark" aria-hidden="true">${icons.info}</div>
      <p>imhere</p>
    </div>
  `;
}

// state.authModeに応じてログイン/新規登録フォームを切り替えます。
export function authTemplate() {
  const isLogin = state.authMode === "login";

  return `
    <main class="auth-page">
      <section class="auth-panel" aria-labelledby="auth-title">
        <div class="auth-brand">
          <div class="brand-mark" aria-hidden="true">${icons.info}</div>
          <h1 id="auth-title">imhere</h1>
          <p>${isLogin ? "アカウントにログイン" : "新しいアカウントを作成"}</p>
        </div>

        <div class="segmented" role="tablist" aria-label="認証モード">
          <button class="segment-button ${isLogin ? "is-active" : ""}" type="button" data-action="auth-mode" data-mode="login">ログイン</button>
          <button class="segment-button ${!isLogin ? "is-active" : ""}" type="button" data-action="auth-mode" data-mode="register">新規登録</button>
        </div>

        <div class="auth-card">
          <form class="form" data-auth-form>
            ${!isLogin ? usernameFieldTemplate() : ""}
            ${emailFieldTemplate()}
            ${passwordFieldTemplate(isLogin)}
            ${state.authError ? errorTemplate(state.authError) : ""}
            ${submitButtonTemplate(isLogin)}
          </form>
        </div>
      </section>
    </main>
  `;
}

// 新規登録モードでだけ表示するユーザー名入力です。
function usernameFieldTemplate() {
  return `
    <label class="field">
      <span class="label">ユーザー名</span>
      <input class="input" type="text" name="username" autocomplete="username" placeholder="yamada" maxlength="50">
    </label>
  `;
}

// ログイン/新規登録で共通のメール入力です。
function emailFieldTemplate() {
  return `
    <label class="field">
      <span class="label">メールアドレス</span>
      <input class="input" type="email" name="email" autocomplete="email" placeholder="you@example.com" required>
    </label>
  `;
}

// モードに応じてautocompleteとプレースホルダーを変えます。
function passwordFieldTemplate(isLogin) {
  return `
    <label class="field">
      <span class="field-row">
        <span class="label">パスワード</span>
      </span>
      <input class="input" type="password" name="password" autocomplete="${isLogin ? "current-password" : "new-password"}" placeholder="${isLogin ? "••••••••" : "8文字以上"}" required>
      ${!isLogin ? '<span class="hint">8文字以上で入力してください</span>' : ""}
    </label>
  `;
}

// APIまたは入力検証のエラーをフォーム内に表示します。
function errorTemplate(message) {
  return `
    <div class="error-box" role="alert">
      ${icons.alert}
      <span>${escapeHtml(message)}</span>
    </div>
  `;
}

// 送信中はスピナーと文言を切り替えます。
function submitButtonTemplate(isLogin) {
  return `
    <button class="button button-primary button-full" type="submit" ${state.authLoading ? "disabled" : ""}>
      ${state.authLoading ? '<span class="spinner" aria-hidden="true"></span>' : ""}
      <span>${state.authLoading ? (isLogin ? "ログイン中..." : "登録中...") : (isLogin ? "ログイン" : "アカウントを作成")}</span>
    </button>
  `;
}
