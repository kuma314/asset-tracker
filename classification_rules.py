from __future__ import annotations

from typing import Iterable

from canonicalization import canonical_name

# 追加ルールの例:
# CANONICAL_TO_CATEGORY[canonical_name("eMAXIS Slim 先進国株式")] = ("投資信託", "先進国")

CANONICAL_TO_CATEGORY: dict[str, tuple[str, str]] = {
    canonical_name("ＳＢＩ・Ｖ・Ｓ＆Ｐ５００インデックス・ファンド"): (
        "投資信託",
        "米国株",
    ),
    canonical_name("SBI・V・S&P500インデックス・ファンド"): (
        "投資信託",
        "米国株",
    ),
    canonical_name("eMAXIS Slim 全世界株式"): ("投資信託", "全世界"),
    canonical_name("ｉＴｒｕｓｔインド株式"): ("投資信託", "インド"),
    canonical_name("iFreeNEXT FANG+"): ("投資信託", "米国テック株"),
    canonical_name("NTT"): ("日本株", "個別株"),
    canonical_name("9432 NTT"): ("日本株", "個別株"),
}

PARTIAL_CANONICAL_RULES: Iterable[tuple[str, tuple[str, str]]] = (
    (canonical_name("eMAXIS Slim 全世界株式"), ("投資信託", "全世界")),
)


def apply_classification_rules(
    canonical_key: str,
    major_category: str | None,
    sub_category: str | None,
) -> tuple[str | None, str | None, bool]:
    if canonical_key in CANONICAL_TO_CATEGORY:
        major, sub = CANONICAL_TO_CATEGORY[canonical_key]
        return major, sub, True

    for key, (major, sub) in PARTIAL_CANONICAL_RULES:
        if key and key in canonical_key:
            return major, sub, True

    return major_category, sub_category, False
