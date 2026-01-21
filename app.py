from io import StringIO
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
    detect_report_csv,
    normalize_account_type,
    normalize_import_dataframe,
    parse_quantity,
    parse_report_csv,
    parse_value_jpy,
)
from canonicalization import canonical_name
from classification_rules import apply_classification_rules

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
    "ページ", ["Holdings", "Import/Export", "Dashboard"], index=0
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
        name_or_ticker = str(row.get("name_or_ticker") or "").strip()
        if not name_or_ticker:
            errors.append(f"{idx + 1}行目: 銘柄名が未入力です")
            continue
        canonical_key = canonical_name(name_or_ticker)
        major_category = str(row.get("major_category") or "").strip()
        sub_category = str(row.get("sub_category") or "").strip() or None
        major_category, sub_category, overridden = apply_classification_rules(
            canonical_key, major_category, sub_category
        )
        rows.append(
            {
                "major_category": major_category,
                "sub_category": sub_category,
                "name_or_ticker": name_or_ticker,
                "canonical_key": canonical_key,
                "account_type": normalize_account_type(row.get("account_type"))
                or str(row.get("account_type") or "").strip(),
                "quantity": _parse_quantity(row.get("quantity")),
                "value_jpy": value_jpy,
                "category_overridden": overridden,
            }
        )
    return rows, errors


if page == "Holdings":
    st.title("Holdings")

    holdings_df = _load_holdings(DEFAULT_DB_PATH)
    holdings_df = holdings_df.drop(columns=["canonical_key"], errors="ignore")
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
                        "マージは canonical_key + account_type をキーに更新します。"
                    )

                    if st.button("確定してインポート"):
                        if action == "キャンセル":
                            st.info("インポートをキャンセルしました。")
                        else:
                            try:
                                if action == "置換":
                                    replace_holdings(rows)
                                    st.success("インポートしました。")
                                else:
                                    inserted, updated, skipped = (
                                        upsert_holdings_by_key(rows)
                                    )
                                    st.success(
                                        "インポートしました。"
                                        f" inserted {inserted} / updated {updated}"
                                        f" / skipped {skipped}"
                                    )
                                st.cache_data.clear()
                            except ValueError as exc:
                                st.error(f"インポートに失敗しました: {exc}")
                if not errors and rows:
                    st.subheader("正規化プレビュー")
                    preview_df = pd.DataFrame(rows)
                    st.dataframe(
                        preview_df[
                            [
                                "name_or_ticker",
                                "canonical_key",
                                "major_category",
                                "sub_category",
                                "category_overridden",
                                "account_type",
                                "quantity",
                                "value_jpy",
                            ]
                        ],
                        use_container_width=True,
                    )
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
                            "マージは canonical_key + account_type をキーに更新します。"
                        )

                        if st.button("確定してインポート"):
                            if action == "キャンセル":
                                st.info("インポートをキャンセルしました。")
                            else:
                                try:
                                    if action == "置換":
                                        replace_holdings(rows)
                                        st.success("インポートしました。")
                                    else:
                                        inserted, updated, skipped = (
                                            upsert_holdings_by_key(rows)
                                        )
                                        st.success(
                                            "インポートしました。"
                                            f" inserted {inserted} /"
                                            f" updated {updated} /"
                                            f" skipped {skipped}"
                                        )
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
