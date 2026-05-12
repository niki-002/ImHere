# ImHere

ImHere は、家族や小さなグループ内で「今どうしているか」を共有するための状態共有アプリです。バックエンドは FastAPI、DB は PostgreSQL、認証はメールアドレス・パスワードログインと Google / Apple OAuth を想定しています。

## 作成目的

家族や身近な人の状態を、チャットより軽く確認できる仕組みを作ることを目的にしています。ユーザーはグループに参加し、自分の状態を更新します。グループメンバーには WebSocket で更新が通知されます。

## 主な機能

- ユーザー登録・ログイン
- JWT による認証
- Google / Apple ID トークンによる外部ログイン
- グループ作成・削除
- グループメンバー追加・削除・退会
- 自分の状態更新
- グループ内メンバーの状態一覧取得
- WebSocket による状態更新通知
- ユーザー名・表示名によるユーザー検索

## 技術スタック

### バックエンド

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

### データベース

- PostgreSQL
- psycopg2-binary

### 認証・セキュリティ

- PyJWT
- pwdlib
- Google / Apple OAuth
- CORS 設定

## ディレクトリ構造

```text
ImHere
  ├── api
  │   ├── alembic                 # DBマイグレーション
  │   │   ├── env.py
  │   │   └── versions
  │   ├── core
  │   │   └── config.py           # .env から設定を読み込む
  │   ├── models                  # SQLAlchemyモデル
  │   │   ├── auth.py             # User / OAuthAccount
  │   │   ├── base.py             # Base / utc_now
  │   │   └── operation.py        # Group / GroupMember
  │   ├── router                  # APIエンドポイント
  │   │   ├── auth.py
  │   │   └── operation.py
  │   ├── schemas                 # リクエスト・レスポンス定義
  │   │   ├── auth.py
  │   │   └── operation.py
  │   ├── service                 # 認証・DB操作・業務ロジック
  │   │   ├── auth.py
  │   │   └── operation.py
  │   ├── db.py                   # DB接続とセッション管理
  │   └── main.py                 # FastAPIアプリ作成
  ├── .env.example
  ├── requirements.txt
  └── README.md
```

## セットアップ

### 1. 仮想環境を作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. パッケージをインストール

```bash
pip install -r requirements.txt
```

### 3. PostgreSQL に DB を作成

```bash
createdb imhere
createdb imhere_test
```

### 4. 環境変数を設定

```bash
cp .env.example .env
```

`.env` の `DATABASE_URL`、`SECRET_KEY`、`CORS_ORIGINS`、`FRONTEND_URL` を自分の環境に合わせます。

```env
APP_NAME =
APP_ENV =

DATABASE_URL = 
TEST_DATABASE_URL = 

SECRET_KEY = 
ALGORITHM = 
ACCESS_TOKEN_EXPIRE_MINUTES = 

CORS_ORIGINS = 
FRONTEND_URL = 

GOOGLE_CLIENT_IDS =
GOOGLE_JWKS_URL = 
APPLE_CLIENT_IDS =
APPLE_JWKS_URL =
```

`JWT_ALGORITHM` は `ALGORITHM` という名前でも読み込めます。

### 5. マイグレーションを実行

```bash
python -m alembic -c api/alembic.ini upgrade head
```

### 6. サーバーを起動

```bash
uvicorn api.main:app --reload
```

API ドキュメントは以下で確認できます。

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Alembic

DB スキーマは Alembic で管理します。`main.py` では `create_all()` を使わず、マイグレーション履歴を残す方針です。

現在の head を確認:

```bash
python -m alembic -c api/alembic.ini heads
```

DB に反映:

```bash
python -m alembic -c api/alembic.ini upgrade head
```

モデル変更後に migration を作成:

```bash
python -m alembic -c api/alembic.ini revision --autogenerate -m "change message"
```

SQL だけ確認:

```bash
python -m alembic -c api/alembic.ini upgrade head --sql
```

## 主要エンドポイント

### 認証

- `POST /auth/register`: ユーザー登録
- `POST /auth/login`: ログイン
- `POST /auth/oauth/{provider}`: Google / Apple OAuth ログイン
- `POST /auth/google`: Google ログイン
- `POST /auth/apple`: Apple ログイン
- `GET /auth/me`: ログイン中ユーザー取得

互換用に `/login/register`、`/login`、`/login/me` も残しています。

### グループ・状態

- `GET /groups`: 自分が参加しているグループ一覧
- `GET /groups/{group_id}`: グループ詳細
- `POST /groups`: グループ作成
- `POST /groups/{group_id}/members`: メンバー追加
- `DELETE /groups/{group_id}/members/{username}`: メンバー削除
- `DELETE /groups/{group_id}/leave`: グループ退会
- `DELETE /groups/{group_id}`: グループ削除
- `POST /groups/{group_id}/invite`: 招待リンク作成
- `GET /status`: 自分の状態取得
- `PATCH /status`: 自分の状態更新
- `GET /users/search?name=...`: ユーザー検索
- `WS /ws/groups/{group_id}`: グループ状態更新の WebSocket

## 状態の種類

`PATCH /status` で指定できる状態は以下です。

- `ok`
- `busy`
- `home`
- `out`
- `sleep`
- `sos`

## 認証の考え方

通常ログインではメールアドレスとパスワードを使います。パスワードは平文保存せず、`pwdlib` の推奨 hasher でハッシュ化します。

ログイン成功時には JWT を返します。API 呼び出しでは以下のどちらかで token を渡します。

```http
Authorization: Bearer <access_token>
```

または cookie:

```text
access_token=<access_token>
login_token=<access_token>
```

## Google / Apple OAuth

Google / Apple ログインでは、フロントエンドから送られた `id_token` をバックエンドで検証します。

`.env` に client id が未設定の場合、OAuth ログインは `503` で止まります。

```env
GOOGLE_CLIENT_IDS=
APPLE_CLIENT_IDS=
```

複数の client id を許可する場合はカンマ区切りで設定します。

```env
GOOGLE_CLIENT_IDS=
```

`GOOGLE_JWKS_URL` と `APPLE_JWKS_URL` は ID トークンの署名検証に使います。外部認証を使わない場合は client id を空のままにしておけます。

## DB設計

### `users`

ユーザー本体のテーブルです。通常ログイン用の `password_hash`、現在の状態 `current_status`、状態更新日時 `status_updated_at` を持ちます。

### `oauth_accounts`

Google / Apple など外部認証アカウントのテーブルです。`provider` と `provider_user_id` の組み合わせをユニークにし、外部サービス上のユーザーIDを安全に管理します。

### `groups`

グループ本体のテーブルです。`owner_id` で作成者を持ちます。

### `group_members`

グループとユーザーをつなぐ中間テーブルです。`group_id` と `user_id` の組み合わせをユニークにし、同じユーザーが同じグループに重複参加しないようにしています。

## 設計方針

- ユーザー本体は `users` に集約する
- 外部ログイン固有の情報は `oauth_accounts` に分ける
- グループ参加関係は `group_members` で表現する
- DB スキーマ変更は Alembic migration として履歴を残す
- URL、秘密鍵、CORS、OAuth 設定は `.env` に置く

## 開発時の確認コマンド

```bash
python -m compileall api
python -m alembic -c api/alembic.ini heads
python -m alembic -c api/alembic.ini upgrade head --sql
pytest
```

現在テストファイルが無い場合、`pytest` は `collected 0 items` になります。

## よくあるエラー

### `DATABASE_URL is required`

`.env` に `DATABASE_URL` が設定されていません。PostgreSQL の接続URLを設定してください。

### `SECRET_KEY must be at least 32 characters in production`

`APP_ENV=production` の場合、`SECRET_KEY` は32文字以上にしてください。

### `GOOGLE_CLIENT_IDS が設定されていません`

Google ログインを使う場合は、Google Cloud Console で発行した client id を `GOOGLE_CLIENT_IDS` に設定してください。Google ログインを使わない場合は、このエンドポイントを呼ばなければ問題ありません。

### CORS でフロントエンドから呼べない

フロントエンドの URL を `CORS_ORIGINS` に追加してください。

```env
CORS_ORIGINS=
```