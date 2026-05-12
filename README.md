# ImHere

ImHereは、グループ内のメンバーの状態を共有するためのアプリです。バックエンドはFastAPI、フロントエンドは依存なしのHTML/CSS/JavaScriptで実装しています。

## 技術スタック

- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: SQLite または PostgreSQL
- Auth: メール/パスワード認証, JWT Bearer Token
- Frontend: HTML, CSS, JavaScript ES Modules
- Realtime: WebSocket

## ディレクトリ構成

```text
ImHere/
├── api/
│   ├── main.py              # FastAPIアプリの作成とルーター登録
│   ├── db.py                # SQLAlchemyエンジン/セッション
│   ├── core/config.py       # 環境変数の読み込みと検証
│   ├── models/              # SQLAlchemyモデル
│   ├── schemas/             # Pydanticスキーマ
│   ├── service/             # 認証/グループ/ステータスの業務ロジック
│   ├── router/              # APIエンドポイント
│   └── alembic/             # DBマイグレーション
├── frontend/
│   ├── index.html           # フロントエンド入口
│   ├── css/                 # 画面/機能別CSS
│   └── js/                  # 状態管理、API、イベント、テンプレート
├── requirements.txt
└── .env.example
```

## セットアップ

### 1. 仮想環境と依存関係

```bash
cd /home/niki02/ImHere
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数

`.env.example`を参考に`.env`を作成します。

```env
APP_NAME=ImHere API
APP_ENV=development

DATABASE_URL=sqlite:///./imhere.sqlite3
SECRET_KEY=development-secret-key-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
FRONTEND_URL=http://127.0.0.1:5173
```

PostgreSQLを使う場合は、`DATABASE_URL`を次のような形式にします。

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/imhere
```

### 3. DBマイグレーション

```bash
alembic -c api/alembic.ini upgrade head
```

### 4. バックエンド起動

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

APIドキュメントは次で確認できます。

```text
http://127.0.0.1:8000/docs
```

### 5. フロントエンド起動

ES Modulesを使っているため、HTMLファイルを直接開くのではなくHTTPサーバーで配信します。

```bash
python3 -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

ブラウザで開きます。

```text
http://127.0.0.1:5173/
```

フロントエンドのAPI接続先は既定で`http://localhost:8000`です。変更したい場合はブラウザのコンソールで設定できます。

```js
localStorage.setItem("imhere_api_base", "http://127.0.0.1:8000");
```

## 主なAPI

### 認証

- `POST /auth/register`  
  新規登録し、アクセストークンを返します。

- `POST /auth/login`  
  メールアドレスとパスワードでログインします。

- `GET /auth/me`  
  現在ログイン中のユーザー情報を返します。

### グループ

- `GET /groups`  
  自分が所属するグループ一覧を取得します。

- `POST /groups`  
  グループを作成します。

- `DELETE /groups/{group_id}`  
  オーナーがグループを削除します。

- `DELETE /groups/{group_id}/leave`  
  グループから退会します。

- `POST /groups/{group_id}/members`  
  ユーザー名でメンバーを追加します。

- `DELETE /groups/{group_id}/members/{username}`  
  オーナーがメンバーを削除します。

### ステータス

- `GET /status`  
  自分の現在ステータスを取得します。

- `PATCH /status`  
  自分のステータスを更新します。

使用できるステータス:

```text
ok, home, busy, out, sleep, sos
```

### ユーザー検索

- `GET /users/search?name={query}`  
  招待用にユーザー名または表示名でユーザーを検索します。

### WebSocket

- `WS /ws/groups/{group_id}?token={access_token}`  
  グループ内のステータス更新をリアルタイムに受信します。

## フロントエンド構成

フロントエンドは小さなSPAとして作っています。`index.html`の`#app`にJavaScriptで画面を描画します。

```text
frontend/js/
├── main.js                 # 起動入口
├── actions.js              # DOMイベントの振り分け
├── state.js                # アプリ全体の状態
├── api.js                  # fetch共通処理
├── session.js              # トークン/ユーザー保存
├── render.js               # stateから画面を再描画
├── websocket.js            # グループWebSocket
├── services/               # 認証、データ取得、グループ、招待、ステータス
└── templates/              # 画面HTMLの生成
```

CSSは機能ごとに分割し、`frontend/css/main.css`から読み込みます。

```text
frontend/css/
├── main.css                # CSS入口
├── tokens.css              # 色、状態色、共通変数
├── base.css                # 共通部品
├── auth.css                # 認証画面
├── shell.css               # アプリ全体レイアウト
├── groups.css              # グループ一覧/見出し
├── people.css              # 招待/ユーザーメニュー
├── status.css              # ステータスチップ
├── members.css             # メンバーカード
├── modal.css               # グループ作成モーダル
└── responsive.css          # レスポンシブ調整
```

## 開発メモ

- フロントエンドはビルド不要です。
- API通信には`Authorization: Bearer <token>`を使います。
- トークンは`localStorage`とCookieに保存します。
- WebSocketは選択中グループに合わせて接続先を切り替えます。
- CORS設定にフロントエンドのURLを必ず含めてください。

## よく使うコマンド

```bash
# バックエンド起動
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# フロントエンド起動
python3 -m http.server 5173 --bind 127.0.0.1 --directory frontend

# DBマイグレーション
alembic -c api/alembic.ini upgrade head

# JS構文チェック
find frontend/js -name '*.js' -exec node --check {} \;
```
