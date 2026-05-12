// フロント全体で共有する固定値をまとめます。
// API URLは window 変数、localStorage、デフォルト値の順で決めます。
export const API_BASE = (
  window.IMHERE_API_BASE ||
  localStorage.getItem("imhere_api_base") ||
  "http://localhost:8000"
).replace(/\/$/, "");

// ログイン状態を保存するキーとCookieの寿命です。
export const TOKEN_KEY = "imhere_access_token";
export const USER_KEY = "imhere_user";
export const COOKIE_MAX_AGE = 60 * 60 * 24 * 7;

// バックエンドの StatusType と対応する表示情報です。
export const STATUS_OPTIONS = [
  { type: "ok", label: "元気", emoji: "😊" },
  { type: "home", label: "在宅", emoji: "🏠" },
  { type: "busy", label: "忙しい", emoji: "⚡" },
  { type: "out", label: "外出中", emoji: "🚶" },
  { type: "sleep", label: "就寝", emoji: "😴" },
  { type: "sos", label: "SOS", emoji: "🆘" },
];

// グループ作成モーダルで選べるアイコン候補です。
export const EMOJI_OPTIONS = [
  "🏠",
  "⭐",
  "💼",
  "🎮",
  "🎵",
  "📚",
  "🌸",
  "🍜",
  "🏃",
  "🎨",
  "✈️",
  "👥",
];
