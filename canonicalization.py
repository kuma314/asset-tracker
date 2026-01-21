from __future__ import annotations

import re
import unicodedata


_SYMBOL_PATTERN = re.compile(
    r"[・･·&＆/／()（）\[\]【】{}<>＜＞:：;；,，.．、。!?！？＝=＋+×＊*〜～\-‐‑–—―−]+"
)


def canonical_name(value: object | None) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text).upper()

    if "EMAXIS SLIM" in text and "全世界株式" in text:
        text = re.sub(
            r"[（(]?オール[\s・-]*カントリー[)）]?",
            "",
            text,
        )

    text = _SYMBOL_PATTERN.sub(" ", text)
    text = " ".join(text.split())
    return text.replace(" ", "")
