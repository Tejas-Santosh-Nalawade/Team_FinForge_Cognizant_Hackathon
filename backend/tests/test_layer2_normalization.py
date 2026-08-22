from backend.app.core.normalization.coa_mapper import CanonicalMapper
from backend.app.core.parser.spell_checker import FinancialSpellChecker


def test_context_aware_mapping():
    m = CanonicalMapper()
    assert m.map_label("Gross Revenues", "income_statement").canonical == "revenue"
    assert m.map_label("Trade Debtors", "balance_sheet").canonical == "accounts_receivable_net"
    assert m.map_label("Net Income", "cash_flow_statement").canonical == "net_income_starting"
    assert m.map_label("Net Income", "income_statement").canonical == "net_income"


def test_typo_and_unknown_safety():
    m = CanonicalMapper()
    typo = m.map_label("Acounts Recievable Net", "balance_sheet")
    assert typo.status == "MAPPED"
    unknown = m.map_label("Quantum Synergy Reserve Adjustment", "balance_sheet")
    assert unknown.status == "UNMAPPED"


def test_financial_spell_checker():
    issues = FinancialSpellChecker().check_text("Acounts recievable  increased increased during the period.")
    types = {i["issue_type"] for i in issues}
    assert "FINANCIAL_SPELLING" in types
    assert "GRAMMAR" in types


def test_multi_entity_additive_consolidation(tmp_path):
    from backend.app.core.normalization.layer2_gateway import Layer2Gateway

    for entity, assets, liabilities, equity in [
        ("Entity_A", 100.0, 60.0, 40.0),
        ("Entity_B", 250.0, 150.0, 100.0),
    ]:
        folder = tmp_path / "entities" / entity / "current_data"
        folder.mkdir(parents=True)
        (folder / "balance_sheet.csv").write_text(
            "Total Assets,%s\nTotal Liabilities,%s\nTotal Equity,%s\n" % (assets, liabilities, equity),
            encoding="utf-8",
        )

    result = Layer2Gateway().run(
        [tmp_path],
        client_name="Group Holdings",
        period="2026-03-31",
        comparative_period="2025-03-31",
        currency="USD",
        scale="MILLIONS",
    )
    bs = result["financial_statements"]["current_data"]["balance_sheet"]
    assert bs["total_assets"] == 350.0
    assert bs["total_liabilities"] == 210.0
    assert bs["total_equity"] == 140.0
    consolidation = result["normalization_report"]["consolidation"]
    assert consolidation["mode"] == "MULTI_ENTITY_ADDITIVE"
    assert consolidation["entity_count"] == 2
