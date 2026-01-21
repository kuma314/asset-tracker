from io import StringIO
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from db import (
    DEFAULT_DB_PATH,
    delete_holding,
    fetch_holdings,
    init_db,
    insert_holdings,
    replace_holdings,
    summarize_by,
    top_holdings,
    upsert_holdings_by_key,
    upsert_holding,
)
from parsing import (
    build_name_or_ticker,
    detect_report_csv,
    normalize_account_type,
    normalize_import_dataframe,
    normalize_name,
    normalize_ticker,
    parse_quantity,
    parse_report_csv,
    parse_value_jpy,
)
from screenshot_import import extract_holdings_from_screenshot

REQUIRED_COLUMNS = [
    "major_category",
    "sub_category",
    "name_or_ticker",
    "account_type",
    "quantity",
    "value_jpy",
]


st.set_page_config(page_title="Asset Tracker", layout="wide")

init_db(DEFAULT_DB_PATH)


st.sidebar.title("Asset Tracker")
page = st.sidebar.radio(
    "ページ", ["Holdings", "Import/Export", "Screenshot Import", "Dashboard"], index=0
)


@st.cache_data
def _load_holdings(db_path: Path) -> pd.DataFrame:
    rows = fetch_holdings(db_path)
    if not rows:
        return pd.DataFrame(columns=["id", *REQUIRED_COLUMNS, "updated_at"])
    data = [dict(row) for row in rows]
    return pd.DataFrame(data)


def _parse_quantity(value) -> float | None:
    return parse_quantity(value)


def _build_rows_from_df(df: pd.DataFrame) -> tuple[list[dict], list[str]]:
    rows = []
    errors = []
    for idx, row in df.iterrows():
        value_jpy = parse_value_jpy(row.get("value_jpy"))
        if value_jpy is None:
            errors.append(f"{idx + 1}行目: 評価額(円)が未入力です")
            continue
        rows.append(
            {
                "major_category": str(row.get("major_category") or "").strip(),
                "sub_category": str(row.get("sub_category") or "").strip() or None,
                "name_or_ticker": str(row.get("name_or_ticker") or "").strip(),
                "account_type": str(row.get("account_type") or "").strip(),
                "quantity": _parse_quantity(row.get("quantity")),
                "value_jpy": value_jpy,
            }
        )
    return rows, errors


if page == "Holdings":
    st.title("Holdings")

    holdings_df = _load_holdings(DEFAULT_DB_PATH)
    all_major_categories = sorted(
        value for value in holdings_df["major_category"].dropna().unique()
    )
    all_account_types = sorted(
        value for value in holdings_df["account_type"].dropna().unique()
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        major_filter = st.selectbox(
            "大分類フィルタ", ["All", *all_major_categories]
        )
    with col2:
        account_filter = st.selectbox(
            "口座区分フィルタ", ["All", *all_account_types]
        )
    with col3:
        st.caption(f"DB: {DEFAULT_DB_PATH}")

    filtered = holdings_df.copy()
    if major_filter != "All":
        filtered = filtered[filtered["major_category"] == major_filter]
    if account_filter != "All":
        filtered = filtered[filtered["account_type"] == account_filter]

    total_value = filtered["value_jpy"].fillna(0).sum()
    st.metric("評価額合計 (円)", f"{int(total_value):,}")

    editable = filtered.copy()
    if "delete" not in editable.columns:
        editable.insert(0, "delete", False)

    with st.form("holdings_editor"):
        edited = st.data_editor(
            editable,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID", disabled=True, help="編集不可"
                ),
                "updated_at": st.column_config.TextColumn(
                    "更新日時", disabled=True
                ),
                "value_jpy": st.column_config.NumberColumn(
                    "評価額(円)", min_value=0, step=100
                ),
            },
        )
        submitted = st.form_submit_button("保存")

    if submitted:
        errors = []
        for _, row in edited.iterrows():
            if row.get("delete") is True:
                if pd.notna(row.get("id")):
                    delete_holding(int(row["id"]))
                continue

            is_blank = all(
                pd.isna(row.get(col)) or row.get(col) == ""
                for col in [
                    "major_category",
                    "name_or_ticker",
                    "account_type",
                    "value_jpy",
                ]
            )
            if is_blank:
                continue

            try:
                value_jpy = parse_value_jpy(row.get("value_jpy"))
                if value_jpy is None:
                    raise ValueError("value_jpy is required")
                upsert_holding(
                    holding_id=int(row["id"]) if pd.notna(row.get("id")) else None,
                    major_category=str(row.get("major_category") or "").strip(),
                    sub_category=str(row.get("sub_category") or "").strip()
                    or None,
                    name_or_ticker=str(row.get("name_or_ticker") or "").strip(),
                    account_type=str(row.get("account_type") or "").strip(),
                    quantity=_parse_quantity(row.get("quantity")),
                    value_jpy=value_jpy,
                )
            except (ValueError, TypeError) as exc:
                errors.append(str(exc))

        if errors:
            st.error("保存に失敗しました: " + "; ".join(errors))
        else:
            st.success("保存しました。再読み込みしてください。")
            st.cache_data.clear()

elif page == "Import/Export":
    st.title("Import / Export")

    st.subheader("CSVアップロード")
    uploaded = st.file_uploader("CSVファイル", type=["csv"])

    if uploaded is not None:
        uploaded_bytes = uploaded.getvalue()
        try:
            is_report, decoded_text = detect_report_csv(uploaded_bytes)
        except ValueError as exc:
            st.error(str(exc))
            decoded_text = None
            is_report = False

        if decoded_text is not None and is_report:
            try:
                report_df = parse_report_csv(uploaded_bytes)
            except ValueError as exc:
                st.error(f"CSVの解析に失敗しました: {exc}")
                report_df = None

            if report_df is not None:
                st.caption("保有証券一覧レポート形式を検出しました。")
                st.subheader("プレビュー (編集可能)")
                edited_df = st.data_editor(
                    report_df,
                    num_rows="dynamic",
                    use_container_width=True,
                )
                rows, errors = _build_rows_from_df(edited_df)
                if errors:
                    st.error("インポート前の確認でエラーが見つかりました。")
                    st.write("\n".join(errors[:10]))
                else:
                    total_value = sum(row["value_jpy"] for row in rows)
                    st.metric("取り込み件数", f"{len(rows):,}")
                    st.metric("評価額合計 (円)", f"{int(total_value):,}")

                    action = st.radio(
                        "既存データの扱い",
                        ["キャンセル", "置換", "マージ"],
                        index=0,
                        horizontal=True,
                    )
                    st.caption(
                        "マージは major_category + name_or_ticker + account_type をキーに更新します。"
                    )

                    if st.button("確定してインポート"):
                        if action == "キャンセル":
                            st.info("インポートをキャンセルしました。")
                        else:
                            try:
                                if action == "置換":
                                    replace_holdings(rows)
                                else:
                                    upsert_holdings_by_key(rows)
                                st.success("インポートしました。")
                                st.cache_data.clear()
                            except ValueError as exc:
                                st.error(f"インポートに失敗しました: {exc}")
        elif decoded_text is not None:
            try:
                uploaded_df = pd.read_csv(StringIO(decoded_text))
            except Exception as exc:
                st.error(f"CSVの読み込みに失敗しました: {exc}")
                uploaded_df = None

            if uploaded_df is not None:
                normalized_df = normalize_import_dataframe(uploaded_df)
                missing = [
                    col for col in REQUIRED_COLUMNS if col not in normalized_df.columns
                ]
                if missing:
                    st.error(
                        f"CSVに必要な列が不足しています: {', '.join(missing)}"
                    )
                else:
                    rows, errors = _build_rows_from_df(normalized_df)

                    if errors:
                        st.error("インポート前の確認でエラーが見つかりました。")
                        st.write("\n".join(errors[:10]))
                    else:
                        preview_df = pd.DataFrame(rows)
                        total_value = sum(row["value_jpy"] for row in rows)
                        st.metric("取り込み件数", f"{len(rows):,}")
                        st.metric("評価額合計 (円)", f"{int(total_value):,}")
                        st.subheader("プレビュー (先頭10行)")
                        st.dataframe(preview_df.head(10), use_container_width=True)

                        action = st.radio(
                            "既存データの扱い",
                            ["キャンセル", "置換", "マージ"],
                            index=0,
                            horizontal=True,
                        )
                        st.caption(
                            "マージは major_category + name_or_ticker + account_type をキーに更新します。"
                        )

                        if st.button("確定してインポート"):
                            if action == "キャンセル":
                                st.info("インポートをキャンセルしました。")
                            else:
                                try:
                                    if action == "置換":
                                        replace_holdings(rows)
                                    else:
                                        upsert_holdings_by_key(rows)
                                    st.success("インポートしました。")
                                    st.cache_data.clear()
                                except ValueError as exc:
                                    st.error(f"インポートに失敗しました: {exc}")

    st.divider()
    st.subheader("CSVダウンロード")
    export_df = _load_holdings(DEFAULT_DB_PATH)
    export_df = export_df[REQUIRED_COLUMNS]
    csv_data = export_df.to_csv(index=False)
    st.download_button(
        "現在のデータをダウンロード",
        data=csv_data,
        file_name="holdings.csv",
        mime="text/csv",
    )

elif page == "Screenshot Import":
    st.title("Screenshot Import")
    st.caption("米国株のスクリーンショット画像を解析して保有情報を取り込みます。")

    uploaded = st.file_uploader(
        "スクリーンショット画像", type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded is None:
        st.session_state.pop("screenshot_rows", None)
    else:
        st.image(uploaded, caption="アップロード済み画像", use_column_width=True)

    if uploaded is not None and st.button("解析する"):
        with st.spinner("画像を解析しています..."):
            try:
                rows = extract_holdings_from_screenshot(
                    uploaded.getvalue(), os.getenv("OPENAI_API_KEY", "")
                )
            except Exception as exc:
                st.error(f"解析に失敗しました: {exc}")
                rows = []

        if not rows:
            st.warning("米国株の行が見つかりませんでした。")
        else:
            st.session_state["screenshot_rows"] = rows

    if "screenshot_rows" in st.session_state:
        st.subheader("プレビュー (編集可能)")
        preview_df = pd.DataFrame(st.session_state["screenshot_rows"])
        edited_df = st.data_editor(
            preview_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "ticker": st.column_config.TextColumn("ティッカー"),
                "name": st.column_config.TextColumn("銘柄名"),
                "quantity": st.column_config.NumberColumn("保有数量"),
                "avg_cost": st.column_config.NumberColumn("取得単価"),
                "last_price": st.column_config.NumberColumn("現在値"),
                "value_jpy": st.column_config.NumberColumn("円換算評価額"),
                "account_type": st.column_config.TextColumn("口座区分"),
                "name_or_ticker": st.column_config.TextColumn(
                    "内部用", disabled=True
                ),
            },
        )

        replace_mode = st.checkbox("既存データを置換（全削除→投入）", value=False)
        if st.button("DBへ反映（upsert）"):
            rows = []
            errors = []
            for idx, row in edited_df.iterrows():
                ticker = normalize_ticker(row.get("ticker"))
                if not ticker:
                    errors.append(f"{idx + 1}行目: ティッカーが必要です。")
                    continue
                name = normalize_name(row.get("name"))
                name_or_ticker = build_name_or_ticker(ticker, name)
                account_type = normalize_account_type(row.get("account_type")) or "不明"
                quantity = parse_quantity(row.get("quantity"))
                try:
                    value_jpy = parse_value_jpy(row.get("value_jpy"))
                except ValueError as exc:
                    errors.append(f"{idx + 1}行目: {exc}")
                    continue

                rows.append(
                    {
                        "major_category": "米国株",
                        "sub_category": "個別株",
                        "name_or_ticker": name_or_ticker,
                        "account_type": account_type,
                        "quantity": quantity,
                        "value_jpy": value_jpy,
                    }
                )

            if errors:
                st.error("反映に失敗しました: " + "; ".join(errors[:10]))
            else:
                try:
                    if replace_mode:
                        replace_holdings(rows)
                    else:
                        upsert_holdings_by_key(rows)
                    st.success("DBへ反映しました。")
                    st.cache_data.clear()
                except ValueError as exc:
                    st.error(f"反映に失敗しました: {exc}")

else:
    st.title("Dashboard")

    st.subheader("大分類別の合計")
    major_summary = summarize_by("major_category", DEFAULT_DB_PATH)
    if major_summary:
        major_df = pd.DataFrame(major_summary)
        st.bar_chart(major_df.set_index("label"))
    else:
        st.info("データがありません")

    st.subheader("口座区分別の合計")
    account_summary = summarize_by("account_type", DEFAULT_DB_PATH)
    if account_summary:
        account_df = pd.DataFrame(account_summary)
        st.bar_chart(account_df.set_index("label"))
    else:
        st.info("データがありません")

    st.subheader("上位銘柄 (評価額順 Top 10)")
    top_rows = top_holdings(10, DEFAULT_DB_PATH)
    if top_rows:
        top_df = pd.DataFrame(top_rows)
        st.dataframe(top_df, use_container_width=True)
    else:
        st.info("データがありません")
