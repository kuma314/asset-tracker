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

## OPENAI_API_KEY

スクリーンショット取り込み（Screenshot Import）ではOpenAI APIを使用します。

Codespaces の **Settings** → **Secrets and variables** → **Codespaces** から
`OPENAI_API_KEY` を登録し、Codespace を再起動してください。

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
`value_jpy` は必須で、0以上の整数です（Screenshot Importで未取得の場合は空欄になることがあります）。

## Screenshot Import

1. サイドバーの「Screenshot Import」を開きます。
2. 証券口座のスクリーンショット画像をアップロードします。
3. 「解析する」を押してプレビューを確認し、必要に応じて編集します。
4. 「DBへ反映（upsert）」で holdings に反映します（置換モードも選択可能）。

個人情報が映り込む場合は、事前にトリミングしてからアップロードすることを推奨します。

## テスト

```bash
pytest
```
