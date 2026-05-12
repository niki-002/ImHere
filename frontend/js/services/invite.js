// メンバー招待のユーザー検索と追加処理を担当します。
import { api } from "../api.js";
import { render } from "../render.js";
import { state } from "../state.js";
import { showToast } from "../toast.js";
import { getActiveGroup } from "../utils.js";
import { loadGroups } from "./data.js";

let searchTimer = null;

// 入力のたびに即APIを叩かず、少し待ってから検索します。
export function scheduleUserSearch(query) {
  if (searchTimer) window.clearTimeout(searchTimer);
  state.selectedCandidate = null;

  if (!query.trim()) {
    state.inviteCandidates = [];
    state.searchingUsers = false;
    return;
  }

  searchTimer = window.setTimeout(searchUsers, 280);
}

// 検索候補を選択し、招待に使うusernameを入力欄へ反映します。
export function selectCandidate(userId) {
  const selected = state.inviteCandidates.find((user) => Number(user.id) === userId);
  if (!selected) return;

  state.selectedCandidate = selected;
  state.inviteQuery = selected.username;
  state.inviteCandidates = [];
  state.focusSelector = '[data-field="invite-query"]';
  render();
}

// 選択済み候補を外して、検索入力を空に戻します。
export function clearSelectedCandidate() {
  state.selectedCandidate = null;
  state.inviteQuery = "";
  state.inviteCandidates = [];
  state.focusSelector = '[data-field="invite-query"]';
  render();
}

// 選択中グループへusernameをメンバーとして追加します。
export async function inviteUser() {
  const activeGroup = getActiveGroup(state);
  if (!activeGroup || state.inviting) return;

  const username = (state.selectedCandidate?.username || state.inviteQuery).trim();
  if (!username) {
    showToast("ユーザー名を入力してください");
    return;
  }

  state.inviting = true;
  render();

  try {
    await api(`/groups/${activeGroup.id}/members`, {
      method: "POST",
      body: JSON.stringify({ username }),
    });

    showToast("メンバーを追加しました");
    closeInviteStateOnly();
    await loadGroups();
  } catch (error) {
    showToast(error.message || "招待に失敗しました");
  } finally {
    state.inviting = false;
    render();
  }
}

// 現在入力されている検索語でユーザー候補を取得します。
async function searchUsers() {
  const currentQuery = state.inviteQuery.trim();
  if (!currentQuery) return;

  state.searchingUsers = true;
  state.focusSelector = '[data-field="invite-query"]';
  render();

  try {
    const users = await api(`/users/search?name=${encodeURIComponent(currentQuery)}`);

    // 古い検索結果が後から返ってきた場合は反映しません。
    if (state.inviteQuery.trim() === currentQuery) {
      state.inviteCandidates = Array.isArray(users) ? users : [];
    }
  } catch {
    state.inviteCandidates = [];
  } finally {
    state.searchingUsers = false;
    state.focusSelector = '[data-field="invite-query"]';
    render();
  }
}

// 招待完了後にポップオーバー内の状態だけを初期化します。
function closeInviteStateOnly() {
  state.inviteOpen = false;
  state.inviteQuery = "";
  state.inviteCandidates = [];
  state.selectedCandidate = null;
}
