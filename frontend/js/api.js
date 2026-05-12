import { API_BASE } from "./constants.js";
import { state } from "./state.js";
import { parseJson } from "./utils.js";

// fetch失敗時にHTTPステータスとレスポンス本文を持たせるための専用エラーです。
export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

// ImHere APIへの共通リクエスト関数です。
// 認証が必要なAPIではBearerトークンを自動で付与します。
export async function api(path, options = {}, requiresAuth = true) {
  const headers = new Headers(options.headers || {});

  // JSON bodyを渡す呼び出しではContent-Typeを補います。
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (requiresAuth && state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  // Cookie認証にも対応できるよう、credentialsも常に付けています。
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  const text = await response.text();
  const payload = text ? parseJson(text) : null;

  // FastAPIの detail を優先して、画面に出せるエラーへ整形します。
  if (!response.ok) {
    const detail = payload && typeof payload.detail === "string" ? payload.detail : "";
    throw new ApiError(detail || "リクエストに失敗しました", response.status, payload);
  }

  return payload;
}
