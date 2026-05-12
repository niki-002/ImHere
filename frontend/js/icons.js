// 外部アイコンライブラリを使わず、必要なSVGだけを文字列として保持します。
// テンプレート側では icons.add のように差し込んで使います。
export const icons = {
  add: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M11 5h2v6h6v2h-6v6h-2v-6H5v-2h6V5Z"></path></svg>',
  alert: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2 2 20h20L12 2Zm1 15h-2v-2h2v2Zm0-4h-2V8h2v5Z"></path></svg>',
  close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m6.4 5 12.6 12.6-1.4 1.4L5 6.4 6.4 5Zm12.6 1.4L6.4 19 5 17.6 17.6 5 19 6.4Z"></path></svg>',
  group: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16 11c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3ZM8 11c1.66 0 3-1.34 3-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3Zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13Zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5Z"></path></svg>',
  info: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M11 17h2v-6h-2v6Zm0-8h2V7h-2v2Zm1-7a10 10 0 1 1 0 20 10 10 0 0 1 0-20Z"></path></svg>',
  logout: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M10 17v-2h4v-2h-4v-2l-4 3 4 3Zm-6 4V3h9v2H6v14h7v2H4Zm13-4-1.4-1.4 2.6-2.6H12v-2h6.2l-2.6-2.6L17 7l5 5-5 5Z"></path></svg>',
  search: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m19.6 21-6.3-6.3a7 7 0 1 1 1.4-1.4l6.3 6.3-1.4 1.4ZM9 14a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z"></path></svg>',
  settings: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m19.4 13.5.1-1.5-.1-1.5 2-1.5-2-3.5-2.4 1a9 9 0 0 0-2.6-1.5L14 2h-4l-.4 2.5A9 9 0 0 0 7 6L4.6 5 2.6 8.5l2 1.5-.1 1.5.1 1.5-2 1.5 2 3.5 2.4-1a9 9 0 0 0 2.6 1.5L10 22h4l.4-2.5A9 9 0 0 0 17 18l2.4 1 2-3.5-2-1.5ZM12 15.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7Z"></path></svg>',
  trash: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 21c-.55 0-1-.45-1-1V8H5V6h4V5c0-.55.45-1 1-1h4c.55 0 1 .45 1 1v1h4v2h-1v12c0 .55-.45 1-1 1H7Zm3-4h2v-7h-2v7Zm4 0h2v-7h-2v7Zm-3-11h2V6h-2v0Z"></path></svg>',
};
