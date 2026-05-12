// 自分のステータス変更をAPIへ反映するサービスです。
import { api } from "../api.js";
import { STATUS_OPTIONS } from "../constants.js";
import { render } from "../render.js";
import { state } from "../state.js";
import { showToast } from "../toast.js";
import { statusMeta, updateCurrentUserInGroups } from "../utils.js";
import { loadGroups } from "./data.js";

// 先にUIを切り替え、失敗したら元のステータスへ戻します。
export async function setMyStatus(status) {
  if (!STATUS_OPTIONS.some((item) => item.type === status)) return;

  const previous = state.currentStatus;
  state.currentStatus = status;
  render();

  try {
    const response = await api("/status", {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    state.currentStatus = response.status || status;
    updateCurrentUserInGroups(state, response);
    showToast(`ステータスを「${statusMeta(status).label}」に更新しました`);
    render();
    await loadGroups();
  } catch (error) {
    state.currentStatus = previous;
    showToast(error.message || "ステータス更新に失敗しました");
    render();
  }
}
