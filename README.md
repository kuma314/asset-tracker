# Asset Tracker

ローカルファーストで個人資産を管理するための MVP です。入力・配分・推移・シミュレーション・インポート/エクスポートを一体化し、監査可能なデータ設計を前提にしています。

## 構成

```
backend/   # FastAPI + SQLAlchemy + SQLite + Alembic
frontend/  # React + TypeScript + Vite + Chart.js
```

## セットアップ

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

- DB は `backend/asset_tracker.db` に作成されます。
- `.env.example` を参考に必要な環境変数を指定できます。

### Frontend

```bash
cd frontend
npm install
npm run dev
```

`http://localhost:5173` へアクセスします。

## サンプルデータ投入

```bash
cd backend
python scripts/seed_sample_data.py
```

## API (抜粋)

- `POST /api/accounts`
- `POST /api/instruments`
- `POST /api/valuations`
- `GET /api/portfolio/allocation?date=YYYY-MM-DD&taxonomy=asset_class`
- `GET /api/portfolio/deviation?date=YYYY-MM-DD&taxonomy=asset_class`
- `GET /api/portfolio/timeseries?start=YYYY-MM-DD&end=YYYY-MM-DD&group_by=month`
- `POST /api/simulations/forecast`

## 非機能要件への対応

- ローカルファースト: SQLite をローカルに保存します。
- データ可搬性: インポート/エクスポート画面を用意し、今後 CSV/JSON を接続します。
- 監査可能性: transactions / valuations を分離したスキーマを採用しています。
- テスト: 計算ロジックを `backend/tests` でユニットテストしています。
- 免責表示: UI フッターに固定表示しています。

## テスト

```bash
cd backend
pytest
```
