from __future__ import annotations

import re

from canonicalization import canonicalize_name

RULES: list[tuple[object, str, str, str | None]] = [
    (
        canonicalize_name("SBI・V・S&P500インデックス・ファンド"),
        "投資信託",
        "米国株",
        "SBI・V・S&P500インデックス・ファンド",
    ),
    (
        canonicalize_name("eMAXIS Slim 全世界株式"),
        "投資信託",
        "全世界",
        "eMAXIS Slim 全世界株式",
    ),
    (
        canonicalize_name("iTrust インド株式"),
        "投資信託",
        "インド",
        "iTrust インド株式",
    ),
    (
        canonicalize_name("iFreeNEXT FANG+"),
        "投資信託",
        "米国テック株",
        "iFreeNEXT FANG+",
    ),
    (
        re.compile(r"^(?:\d+\s*)?NTT$"),
        "日本株",
        "個別株",
        "NTT",
    ),
]
