import { COOKIE_MAX_AGE, TOKEN_KEY, USER_KEY } from "./constants.js";

// 保存済みトークンを取得します。なければ未ログイン扱いです。
export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

// 保存済みユーザー情報をJSONとして復元します。
export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// APIトークンはlocalStorageとCookieの両方に保存します。
// CookieはWebSocketやcredentials付きリクエストとの互換用です。
export function persistSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  document.cookie = `access_token=${encodeURIComponent(token)}; Max-Age=${COOKIE_MAX_AGE}; Path=/; SameSite=Lax`;
}

// /auth/me で最新化したユーザーだけを保存し直します。
export function persistUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// ログアウト時にブラウザ側の認証情報をすべて消します。
export function clearStoredSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  document.cookie = "access_token=; Max-Age=0; Path=/; SameSite=Lax";
}
