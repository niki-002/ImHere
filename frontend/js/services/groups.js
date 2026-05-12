// グループとメンバー管理に関するAPI操作をまとめています。
import { api } from "../api.js";
import { EMOJI_OPTIONS } from "../constants.js";
import { render } from "../render.js";
import { state } from "../state.js";
import { showToast } from "../toast.js";
import { connectActiveGroupSocket } from "../websocket.js";
import { loadGroups } from "./data.js";

// グループ作成後は新しいグループを選択状態にします。
export async function createGroup() {
  const name = state.newGroupName.trim();
  if (!name || state.creatingGroup) return;

  state.creatingGroup = true;
  render();

  try {
    const created = await api("/groups", {
      method: "POST",
      body: JSON.stringify({ name, emoji: state.selectedEmoji, color: "bg-zinc-50" }),
    });

    state.groupModalOpen = false;
    state.newGroupName = "";
    state.selectedEmoji = EMOJI_OPTIONS[0];
    state.creatingGroup = false;
    state.activeGroupId = created.id;

    showToast(`「${created.name || name}」グループを作成しました`);
    await loadGroups();
  } catch (error) {
    state.creatingGroup = false;
    showToast(error.message || "グループ作成に失敗しました");
    render();
  }
}

// オーナー用のグループ削除です。
export async function deleteGroup(groupId) {
  const group = state.groups.find((item) => item.id === groupId);
  if (!group || !window.confirm(`「${group.name}」を削除しますか？`)) return;

  try {
    await api(`/groups/${groupId}`, { method: "DELETE" });
    showToast("グループを削除しました");
    await loadGroups();
  } catch (error) {
    showToast(error.message || "グループ削除に失敗しました");
  }
}

// オーナー以外のユーザーがグループから抜ける処理です。
export async function leaveGroup(groupId) {
  const group = state.groups.find((item) => item.id === groupId);
  if (!group || !window.confirm(`「${group.name}」から退会しますか？`)) return;

  try {
    const response = await api(`/groups/${groupId}/leave`, { method: "DELETE" });
    showToast(response?.message || "グループから退会しました");
    await loadGroups();
  } catch (error) {
    showToast(error.message || "グループ退会に失敗しました");
  }
}

// オーナーが指定ユーザーをグループから外す処理です。
export async function removeMember(groupId, username) {
  if (!username || !window.confirm(`@${username} をグループから削除しますか？`)) return;

  try {
    await api(`/groups/${groupId}/members/${encodeURIComponent(username)}`, { method: "DELETE" });
    showToast("メンバーを削除しました");
    await loadGroups();
  } catch (error) {
    showToast(error.message || "メンバー削除に失敗しました");
  }
}

// 選択グループを切り替え、リアルタイム更新の接続先も変えます。
export function selectGroup(groupId) {
  state.activeGroupId = groupId;
  state.inviteOpen = false;
  state.userMenuOpen = false;
  connectActiveGroupSocket(render);
  render();
}
