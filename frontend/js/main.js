// アプリの最小エントリーポイントです。
// 初期化処理は actions.js に寄せ、ここは読み込み順だけを管理します。
import { bindEvents, boot } from "./actions.js";

bindEvents();
boot();
