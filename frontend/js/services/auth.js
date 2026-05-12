// ログイン/新規登録フォームの送信処理を担当します。
import { api } from "../api.js";
import { render } from "../render.js";
import { persistSession } from "../session.js";
import { state } from "../state.js";
import { showToast } from "../toast.js";
import { loadInitialData } from "./data.js";

// フォーム値を検証してから、認証APIへ送信します。
export async function handleAuthSubmit(form) {
  const formData = new FormData(form);
  const email = String(formData.get("email") || "").trim();
  const password = String(formData.get("password") || "");
  const username = String(formData.get("username") || "").trim();

  state.authError = "";

  if (!validateAuthForm({ email, password, username })) {
    render();
    return;
  }

  state.authLoading = true;
  render();

  try {
    const isRegister = state.authMode === "register";

    // 新規登録時はバックエンドのusername/displayName両方へ同じ表示名を送ります。
    const payload = isRegister
      ? { username, displayName: username, email, password }
      : { email, password };

    // 認証APIだけはまだトークンがないためrequiresAuth=falseで呼びます。
    const response = await api(isRegister ? "/auth/register" : "/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }, false);

    if (!response?.access_token) {
      throw new Error("認証トークンの取得に失敗しました");
    }

    state.token = response.access_token;
    state.user = response.user;
    persistSession(response.access_token, response.user);
    state.authLoading = false;

    showToast(isRegister ? "アカウントを作成しました" : "ログインしました");
    await loadInitialData();
  } catch (error) {
    state.authLoading = false;
    state.authError = error.message || "サーバーに接続できませんでした";
    render();
  }
}

// 画面側で先に分かる入力エラーをAPI送信前に止めます。
function validateAuthForm({ email, password, username }) {
  if (state.authMode === "register" && !username) {
    state.authError = "ユーザー名を入力してください";
    return false;
  }
  if (!email) {
    state.authError = "メールアドレスを入力してください";
    return false;
  }
  if (password.length < 8) {
    state.authError = "パスワードは8文字以上で入力してください";
    return false;
  }
  return true;
}
