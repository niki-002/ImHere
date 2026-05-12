import { EMOJI_OPTIONS } from "./constants.js";
import { getStoredToken, getStoredUser } from "./session.js";

// このオブジェクトがアプリ全体の単一の状態です。
// render() は常にこの state を見て画面を再生成します。
export const state = {
  // 起動直後だけローディング画面を表示します。
  booting: true,

  // 認証画面の入力モードと送信状態です。
  authMode: "login",
  authLoading: false,
  authError: "",

  // セッションはlocalStorageから復元します。
  token: getStoredToken(),
  user: getStoredUser(),

  // グループ、選択中グループ、自分のステータスです。
  groups: [],
  activeGroupId: null,
  currentStatus: "ok",
  loadingGroups: false,
  pageError: "",

  // グループ作成モーダルの状態です。
  groupModalOpen: false,
  newGroupName: "",
  selectedEmoji: EMOJI_OPTIONS[0],
  creatingGroup: false,

  // 招待ポップオーバーとユーザー検索の状態です。
  inviteOpen: false,
  inviteQuery: "",
  inviteCandidates: [],
  selectedCandidate: null,
  searchingUsers: false,
  inviting: false,

  // ユーザーメニューと再描画後に戻すフォーカス位置です。
  userMenuOpen: false,
  focusSelector: "",
};
