# ImHere

ImHere は、家族やグループ内で今の状態を共有するための Web アプリです。FastAPI と PostgreSQL を使い、ログイン、グループ管理、ステータス共有を実装しています。

## 主な機能

- ユーザー登録・ログイン
- Google / Apple ログイン
- グループ作成・メンバー管理
- 自分の状態更新
- WebSocket による状態更新通知

## 技術スタック

### バックエンド
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

### データベース
- PostgreSQL

### 認証
- JWT
- pwdlib
- Google / Apple OAuth

## ディレクトリ構造

```text
ImHere
  ├── api
  │   ├── core
  │   │   └── config.py        # 環境変数の読み込み
  │   ├── models               # SQLAlchemyモデル
  │   ├── router               # APIエンドポイント
  │   ├── schemas              # Pydanticスキーマ
  │   ├── service              # DB操作・認証・業務処理
  │   ├── alembic              # マイグレーション
  │   ├── db.py                # DB接続管理
  │   └── main.py              # API起動ファイル
  ├── README.md
  ├── requirements.txt
  └── .env.example
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

### 3. 環境変数を設定

```bash
cp .env.example .env
```

`.env` の `DATABASE_URL` を自分の PostgreSQL に合わせます。

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/imhere
SECRET_KEY=randomstring
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 4. DBを作成

```bash
createdb imhere
```

### 5. マイグレーションを実行

```bash
python -m alembic -c api/alembic.ini upgrade head
```

### 6. サーバーを起動

```bash
uvicorn api.main:app --reload
```

## DB設計

- `users`: ユーザー情報
- `oauth_accounts`: Google / Apple の外部ログイン情報
- `groups`: グループ情報
- `group_members`: グループとユーザーの紐づけ

通常ログインと外部ログインはどちらも `users` に集約し、外部サービス固有のIDだけ `oauth_accounts` に分けています。グループ参加は中間テーブルで管理し、同じユーザーが同じグループに重複参加しないようにしています。

## Alembic

DB のテーブル作成・変更は Alembic で管理します。

```bash
python -m alembic -c api/alembic.ini heads
python -m alembic -c api/alembic.ini revision --autogenerate -m "change message"
python -m alembic -c api/alembic.ini upgrade head
```
