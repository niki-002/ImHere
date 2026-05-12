// 新しいグループを作成するモーダルです。
import { EMOJI_OPTIONS } from "../constants.js";
import { state } from "../state.js";
import { escapeHtml } from "../utils.js";

// 入力中のグループ名と選択中絵文字をstateから反映します。
export function groupModalTemplate() {
  return `
    <div class="modal-backdrop" data-action="close-group-modal">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="group-modal-title" data-modal-panel>
        <h2 id="group-modal-title">新しいグループを作成</h2>
        <form class="form" data-group-form>
          <label class="field">
            <span class="label">グループ名</span>
            <input class="input" type="text" name="groupName" data-field="group-name" value="${escapeHtml(state.newGroupName)}" placeholder="例：大学の友達" maxlength="100" required>
          </label>
          <div class="field">
            <span class="label">アイコンを選ぶ</span>
            <div class="emoji-grid">
              ${EMOJI_OPTIONS.map(emojiButtonTemplate).join("")}
            </div>
          </div>
          <div class="modal-actions">
            <button class="button button-muted" type="button" data-action="close-group-modal">キャンセル</button>
            <button class="button button-primary" type="submit" ${state.creatingGroup || !state.newGroupName.trim() ? "disabled" : ""}>
              ${state.creatingGroup ? '<span class="spinner" aria-hidden="true"></span>' : ""}
              <span>作成する</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  `;
}

// 絵文字候補1つ分の選択ボタンです。
function emojiButtonTemplate(emoji) {
  return `
    <button class="emoji-button ${state.selectedEmoji === emoji ? "is-active" : ""}" type="button" data-action="select-emoji" data-emoji="${escapeHtml(emoji)}">
      ${escapeHtml(emoji)}
    </button>
  `;
}
