// 選択中グループのステータス更新をリアルタイムで受け取ります。
import { API_BASE } from "./constants.js";
import { state } from "./state.js";
import { getActiveGroup, normalizeMembers, parseJson } from "./utils.js";

let socket = null;
let socketGroupId = null;
let socketPingTimer = null;

// activeGroupIdに合わせてWebSocketを張ります。
// すでに同じグループへ接続済みなら何もしません。
export function connectActiveGroupSocket(onRender) {
  const group = getActiveGroup(state);

  if (!group || !state.token) {
    closeSocket();
    return;
  }

  if (socket && socketGroupId === group.id && socket.readyState <= WebSocket.OPEN) {
    return;
  }

  closeSocket();
  socketGroupId = group.id;

  const wsBase = API_BASE.replace(/^http/i, "ws");
  socket = new WebSocket(`${wsBase}/ws/groups/${group.id}?token=${encodeURIComponent(state.token)}`);

  // 接続維持用に定期pingを送ります。
  socket.addEventListener("open", () => {
    socketPingTimer = window.setInterval(() => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send("ping");
      }
    }, 25000);
  });

  // status.updatedだけを受け取り、該当メンバーのカードを更新します。
  socket.addEventListener("message", (event) => {
    const payload = parseJson(event.data);
    if (!payload || payload.type !== "status.updated" || !payload.member) return;

    applyMemberUpdate(payload.groupId, payload.member);
    onRender();
  });

  socket.addEventListener("close", () => {
    if (socketPingTimer) window.clearInterval(socketPingTimer);
    socketPingTimer = null;
  });

  socket.addEventListener("error", closeSocket);
}

// グループ切り替えやログアウト時に接続とpingタイマーを止めます。
export function closeSocket() {
  if (socketPingTimer) window.clearInterval(socketPingTimer);
  socketPingTimer = null;

  if (socket) {
    socket.close();
    socket = null;
  }

  socketGroupId = null;
}

// WebSocketで届いた1人分のメンバー情報をグループ一覧へ反映します。
function applyMemberUpdate(groupId, rawMember) {
  const member = normalizeMembers([rawMember])[0];

  state.groups = state.groups.map((group) => {
    if (group.id !== groupId) return group;

    const exists = group.members.some(
      (item) => item.id === member.id || item.userId === member.userId,
    );

    return {
      ...group,
      members: exists
        ? group.members.map((item) =>
            item.id === member.id || item.userId === member.userId ? member : item,
          )
        : [...group.members, member],
    };
  });
}
