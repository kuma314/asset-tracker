from canonicalization import canonical_name
from classification_rules import apply_classification_rules


def test_canonicalization_handles_fullwidth_and_symbols() -> None:
    left = "ＳＢＩ・Ｖ・Ｓ＆Ｐ５００インデックス・ファンド"
    right = "SBI・V・S&P500 インデックス・ファンド"
    assert canonical_name(left) == canonical_name(right)


def test_canonicalization_emaxis_all_country_variants() -> None:
    with_suffix = "eMAXIS Slim 全世界株式（オール・カントリー）"
    without_suffix = "eMAXIS Slim 全世界株式"
    assert canonical_name(with_suffix) == canonical_name(without_suffix)


def test_classification_rules_apply_to_canonical_key() -> None:
    canonical_key = canonical_name("iFreeNEXT FANG+")
    major, sub, overridden = apply_classification_rules(
        canonical_key, "投資信託", "その他"
    )
    assert (major, sub, overridden) == ("投資信託", "米国テック株", True)
