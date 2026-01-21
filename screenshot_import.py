import base64
import json
from typing import Any

from parsing import (
    build_name_or_ticker,
    normalize_account_type,
    normalize_name,
    normalize_ticker,
    parse_float_value,
    parse_quantity,
    parse_value_jpy,
)

VISION_MODEL = "gpt-4o-mini"

VISION_PROMPT = """あなたは証券口座のスクリーンショットから米国株の保有情報を抽出するアシスタントです。
以下のJSON配列のみを返してください。余計な文章やコードブロックは不要です。
数値はカンマを除去し、- / — / 空欄 は null にしてください。
米国株の行のみを抽出してください。

返却形式:
[
  {
    "ticker": "TSLA",
    "name": "テスラ",
    "quantity": 2,
    "avg_cost": 261.24,
    "last_price": 419.25,
    "value_jpy": 132675,
    "account_type": "NISA(成長)"
  }
]
"""


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("JSONの配列を取得できませんでした。") from None
        payload = json.loads(text[start : end + 1])
    if not isinstance(payload, list):
        raise ValueError("JSONの配列形式ではありません。")
    return payload


def _normalize_vision_row(row: dict[str, Any], index: int) -> dict[str, Any]:
    ticker = normalize_ticker(row.get("ticker"))
    if not ticker:
        raise ValueError(f"{index}行目: ティッカーが見つかりません。")
    name = normalize_name(row.get("name"))
    account_type = normalize_account_type(row.get("account_type")) or "不明"
    quantity = parse_quantity(row.get("quantity"))
    avg_cost = parse_float_value(row.get("avg_cost"))
    last_price = parse_float_value(row.get("last_price"))
    value_jpy = parse_value_jpy(row.get("value_jpy"))
    return {
        "ticker": ticker,
        "name": name or "",
        "quantity": quantity,
        "avg_cost": avg_cost,
        "last_price": last_price,
        "value_jpy": value_jpy,
        "account_type": account_type,
        "name_or_ticker": build_name_or_ticker(ticker, name),
    }


def extract_holdings_from_screenshot(
    image_bytes: bytes,
    api_key: str,
) -> list[dict[str, Any]]:
    if not api_key:
        raise ValueError("OPENAI_API_KEYが設定されていません。")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model=VISION_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": VISION_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "スクリーンショットから米国株の保有情報を抽出してください。",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded}"
                        },
                    },
                ],
            },
        ],
    )
    content = response.choices[0].message.content or ""
    payload = _extract_json_array(content)
    normalized: list[dict[str, Any]] = []
    for idx, row in enumerate(payload, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{idx}行目: JSONの形式が不正です。")
        normalized.append(_normalize_vision_row(row, idx))
    return normalized
