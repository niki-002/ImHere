// 起動時や再読み込み時に必要なデータを取得するサービスです。
import { api, ApiError } from "../api.js";
import { render } from "../render.js";
import { clearStoredSession, persistUser } from "../session.js";
import { state } from "../state.js";
import { showToast } from "../toast.js";
import { normalizeGroups, reconcileActiveGroup } from "../utils.js";
import { closeSocket, connectActiveGroupSocket } from "../websocket.js";

// 保存済みトークンがあればユーザー情報を検証してアプリを復元します。
export async function bootWithStoredSession() {
  if (!state.token) {
    state.booting = false;
    render();
    return;
  }

  try {
    await loadMe();
    if (!state.user) {
      state.booting = false;
      render();
      return;
    }
    await loadInitialData();
  } catch {
    clearSession();
    state.booting = false;
    render();
  }
}

// ログイン直後や起動後に必要な初期データをまとめて取得します。
export async function loadInitialData() {
  state.booting = false;
  state.pageError = "";
  render();

  // どれかが失敗しても残りの取得結果は画面に反映したいためallSettledにしています。
  await Promise.allSettled([loadMe(), loadMyStatus(), loadGroups()]);
  render();
}

// 現在ログイン中のユーザー情報を取得します。
export async function loadMe() {
  try {
    const user = await api("/auth/me");
    state.user = user;
    persistUser(user);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      clearSession();
      state.booting = false;
    } else {
      state.pageError = error.message;
    }
  }
}

// 自分の現在ステータスを取得し、ステータスチップの選択状態に反映します。
export async function loadMyStatus() {
  try {
    const status = await api("/status");
    state.currentStatus = status.status || state.currentStatus;
  } catch (error) {
    if (!(error instanceof ApiError && error.status === 401)) {
      state.pageError = error.message;
    }
  }
}

// 所属グループ一覧を取得し、WebSocket接続も選択グループへ張り直します。
export async function loadGroups() {
  if (!state.token) return;

  state.loadingGroups = true;
  render();

  try {
    const groups = await api("/groups");
    state.groups = normalizeGroups(groups);
    reconcileActiveGroup(state);
    state.pageError = "";
    connectActiveGroupSocket(render);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      clearSession();
      showToast("ログインが必要です");
    } else {
      state.pageError = error.message || "グループ一覧取得に失敗しました";
    }
  } finally {
    state.loadingGroups = false;
    render();
  }
}

// ユーザーメニューの「再読み込み」から呼ばれる軽い更新処理です。
export function refreshData() {
  state.userMenuOpen = false;
  loadGroups();
  loadMyStatus().then(render);
  showToast("再読み込みしました");
}

// 画面状態と保存済みセッションを消してログイン画面へ戻します。
export function logout() {
  clearSession();
  state.authMode = "login";
  state.authError = "";
  state.booting = false;
  showToast("ログアウトしました");
  render();
}

// 認証切れやログアウトで使う共通のセッション破棄処理です。
export function clearSession() {
  state.token = null;
  state.user = null;
  state.groups = [];
  state.activeGroupId = null;
  state.currentStatus = "ok";
  clearStoredSession();
  closeSocket();
}
