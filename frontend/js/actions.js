// DOMイベントを受け取り、該当するサービス処理へ振り分けるファイルです。
// API通信やデータ更新の詳細は services/ 配下へ分離しています。
import { EMOJI_OPTIONS } from "./constants.js";
import { render } from "./render.js";
import { state } from "./state.js";
import { showToast } from "./toast.js";
import { apiBaseLabel } from "./templates/app.js";
import { handleAuthSubmit } from "./services/auth.js";
import { bootWithStoredSession, logout, refreshData } from "./services/data.js";
import {
  createGroup,
  deleteGroup,
  leaveGroup,
  removeMember,
  selectGroup,
} from "./services/groups.js";
import {
  clearSelectedCandidate,
  inviteUser,
  scheduleUserSearch,
  selectCandidate,
} from "./services/invite.js";
import { setMyStatus } from "./services/status.js";
import { closeSocket } from "./websocket.js";

// アプリ全体で使うイベントリスナーを一度だけ登録します。
export function bindEvents() {
  document.addEventListener("submit", handleSubmit);
  document.addEventListener("input", handleInput);
  document.addEventListener("keydown", handleKeydown);
  document.addEventListener("click", handleClick);
  window.addEventListener("beforeunload", closeSocket);
}

// main.js から呼ばれる起動処理です。
export function boot() {
  bootWithStoredSession();
}

// form送信はログイン系とグループ作成の2種類だけを扱います。
async function handleSubmit(event) {
  const authForm = event.target.closest("[data-auth-form]");
  const groupForm = event.target.closest("[data-group-form]");

  if (authForm) {
    event.preventDefault();
    await handleAuthSubmit(authForm);
    return;
  }

  if (groupForm) {
    event.preventDefault();
    await createGroup();
  }
}

// 入力イベントはdata-field属性で対象を判定します。
function handleInput(event) {
  const field = event.target.closest("[data-field]");
  if (!field) return;

  if (field.dataset.field === "group-name") {
    state.newGroupName = field.value;

    // 入力中に作成ボタンのdisabledだけ即時更新し、全体再描画は避けます。
    const submit = document.querySelector("[data-group-form] .button-primary");
    if (submit) submit.disabled = !state.newGroupName.trim() || state.creatingGroup;
  }

  if (field.dataset.field === "invite-query") {
    state.inviteQuery = field.value;
    scheduleUserSearch(state.inviteQuery);
  }
}

// Escapeキーで開いている浮動UIをまとめて閉じます。
function handleKeydown(event) {
  if (event.key !== "Escape") return;

  if (state.groupModalOpen || state.inviteOpen || state.userMenuOpen) {
    state.groupModalOpen = false;
    state.inviteOpen = false;
    state.userMenuOpen = false;
    render();
  }
}

// クリックイベントはdata-action属性をルーティングキーにします。
function handleClick(event) {
  const actionNode = event.target.closest("[data-action]");

  if (!actionNode) {
    closeFloatingPanels(event);
    return;
  }

  const action = actionNode.dataset.action;
  if (isModalInteriorClick(action, event, actionNode)) return;

  routeAction(action, actionNode);
}

// ポップオーバー外側をクリックした時だけ閉じます。
function closeFloatingPanels(event) {
  const clickedFloating = event.target.closest("[data-popover-root]");
  if (clickedFloating || (!state.inviteOpen && !state.userMenuOpen)) return;

  state.inviteOpen = false;
  state.userMenuOpen = false;
  render();
}

// モーダル内クリックが背面クリック扱いにならないようにします。
function isModalInteriorClick(action, event, actionNode) {
  return (
    action === "close-group-modal" &&
    event.target.closest("[data-modal-panel]") &&
    actionNode.classList.contains("modal-backdrop")
  );
}

// data-actionごとに操作を振り分けます。
function routeAction(action, node) {
  switch (action) {
    case "auth-mode":
      switchAuthMode(node.dataset.mode);
      break;
    case "open-group-modal":
      openGroupModal();
      break;
    case "close-group-modal":
      closeGroupModal();
      break;
    case "select-emoji":
      state.selectedEmoji = node.dataset.emoji || EMOJI_OPTIONS[0];
      render();
      break;
    case "select-group":
      selectGroup(Number(node.dataset.groupId));
      break;
    case "delete-group":
      deleteGroup(Number(node.dataset.groupId));
      break;
    case "leave-group":
      leaveGroup(Number(node.dataset.groupId));
      break;
    case "set-status":
      setMyStatus(node.dataset.status);
      break;
    case "toggle-invite":
      toggleInvite();
      break;
    case "close-invite":
      closeInvite();
      break;
    case "select-candidate":
      selectCandidate(Number(node.dataset.userId));
      break;
    case "clear-selected-candidate":
      clearSelectedCandidate();
      break;
    case "invite-user":
      inviteUser();
      break;
    case "remove-member":
      removeMember(Number(node.dataset.groupId), node.dataset.username);
      break;
    case "toggle-user-menu":
      toggleUserMenu();
      break;
    case "refresh-data":
      refreshData();
      break;
    case "show-api-base":
      state.userMenuOpen = false;
      showToast(apiBaseLabel());
      render();
      break;
    case "logout":
      logout();
      break;
    default:
      break;
  }
}

// ログイン/新規登録の切り替え時は古いエラーを消します。
function switchAuthMode(mode) {
  state.authMode = mode === "register" ? "register" : "login";
  state.authError = "";
  render();
}

// モーダルを開いた直後、グループ名入力へフォーカスを戻します。
function openGroupModal() {
  state.groupModalOpen = true;
  state.focusSelector = '[name="groupName"]';
  render();
}

// モーダルを閉じる時は未確定の入力も初期化します。
function closeGroupModal() {
  state.groupModalOpen = false;
  state.newGroupName = "";
  state.selectedEmoji = EMOJI_OPTIONS[0];
  render();
}

// 招待とユーザーメニューは同時に開かないようにします。
function toggleInvite() {
  state.inviteOpen = !state.inviteOpen;
  state.userMenuOpen = false;
  state.focusSelector = state.inviteOpen ? '[data-field="invite-query"]' : "";
  render();
}

// 招待UIを閉じる時は検索状態もまとめて初期化します。
function closeInvite() {
  state.inviteOpen = false;
  state.inviteQuery = "";
  state.inviteCandidates = [];
  state.selectedCandidate = null;
  render();
}

// ユーザーメニューを開く時は招待ポップオーバーを閉じます。
function toggleUserMenu() {
  state.userMenuOpen = !state.userMenuOpen;
  state.inviteOpen = false;
  render();
}
