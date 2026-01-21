# Asset Tracker (MVP)

個人資産の「現在の保有一覧」を記録・閲覧するためのStreamlitアプリです。

## GitHub Codespaces でのセットアップ

1. GitHub上でこのリポジトリを開き、**Code** → **Codespaces** → **Create codespace on main** を選択します。
2. Codespace が起動したら、ターミナルで以下を実行します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
streamlit run app.py
```

起動後、Codespaces の **Ports** タブに表示される URL からアクセスします。

## DB

- SQLiteファイル: `asset_tracker.db`
- リポジトリ直下（`app.py` と同じ階層）に自動作成されます。

## CSV形式

Import/Exportで扱うCSVは以下の列名です。

- `major_category`
- `sub_category`
- `name_or_ticker`
- `account_type`
- `quantity`
- `value_jpy`

`quantity` は空欄でも保存できます（現金など数量がない資産を想定）。
`value_jpy` は必須で、0以上の整数です。

Import時は `name_or_ticker` から正規化した `canonical_key` を生成し、
ルールに合致する銘柄は大分類・中分類を自動で上書きします。

## テスト

```bash
pytest
```
