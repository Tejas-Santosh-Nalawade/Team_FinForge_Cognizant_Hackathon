from pathlib import Path

ROOT = Path("DATASET/True_data/qualitative_corpus")
MDNA = ROOT / "MD&A"
BOARD = ROOT / "Board_Oversight_Memos"

MDNA.mkdir(parents=True, exist_ok=True)
BOARD.mkdir(parents=True, exist_ok=True)

documents = {
MDNA / "prior_period_2024.txt": """PRIOR-PERIOD MD&A COMMENTARY — FY2024
Synthetic test document — non-authoritative.

Financial Performance Context
Revenue increased approximately 8% compared with FY2023. Operating expenses increased approximately 6%, reflecting additional personnel and technology investments.

Working Capital
Accounts Receivable increased approximately 10% compared with the prior period. Management attributed the increase primarily to higher sales volume and a temporary increase in customer payment terms for selected strategic accounts.

Cash Flow
Operating cash flow remained positive, although cash conversion was affected by the increase in trade receivables.

Management Explanation
Management continued to monitor customer collections, overdue balances, and changes in payment behavior. No material deterioration in the overall customer credit profile was identified during the period.

Management Conclusion
Management believes the FY2024 working-capital changes were primarily related to business growth and temporary customer payment-term changes.
""",

MDNA / "prior_period_2025.txt": """PRIOR-PERIOD MD&A COMMENTARY — FY2025
Synthetic test document — non-authoritative.

Financial Performance Context
Revenue increased approximately 11% compared with FY2024. Operating expenses increased approximately 9%, mainly due to higher employee costs and expanded operating capacity.

Working Capital
Accounts Receivable increased approximately 18%, exceeding the rate of revenue growth. Management attributed part of the increase to extended payment terms on selected large customer contracts.

Operating Drivers
Headcount increased approximately 7% during the year to support business expansion. Management continued to evaluate productivity and staffing requirements across operating functions.

Cash Flow
The increase in trade receivables created additional working-capital requirements and temporarily reduced cash conversion.

Management Explanation
Management stated that collection performance remained within expected ranges, while certain large contracts had longer payment cycles than the standard customer terms.

Management Conclusion
Management expects working-capital efficiency to improve as the affected contracts move through their normal billing and collection cycles.
""",

MDNA / "prior_period_2026.txt": """PRIOR-PERIOD MD&A COMMENTARY — FY2026
Synthetic test document — non-authoritative.

Financial Performance Context
Revenue increased approximately 12% compared with FY2025. Operating expenses increased approximately 10%, primarily due to personnel expansion, technology investments, and increased operating activity.

Working Capital
Accounts Receivable increased approximately 38%, materially faster than revenue. Management identified extended customer payment terms from 30 days to 60 days for selected large multi-year contracts as a primary explanation.

Cash Flow
The increase in outstanding trade receivables temporarily increased working-capital requirements because cash collections occurred later under the extended payment terms.

Operating Drivers
Headcount increased approximately 9% to support higher business volumes and customer commitments. Management continued monitoring utilization and staffing efficiency.

Management Explanation
Management continues to monitor customer collections, outstanding invoices, aging trends, and payment behavior for customers receiving extended terms.

Management Conclusion
Management believes the increase in Accounts Receivable relative to Revenue is primarily explained by the temporary impact of extended customer payment terms on selected large multi-year contracts.
""",

BOARD / "board_credit_risk_memo_2024.txt": """BOARD OVERSIGHT MEMO — FY2024 CREDIT RISK REVIEW
Synthetic test document — non-authoritative.

Purpose
This memo summarizes matters presented to the Board regarding credit risk, portfolio quality, and management oversight during FY2024.

Credit Risk
Management reported that overall credit quality remained within the Board-approved risk appetite. Concentrations in selected customer and lending segments were reviewed.

Portfolio Monitoring
Management was asked to continue monitoring delinquency trends, concentration exposure, customer payment behavior, and emerging credit risks.

Liquidity and Capital
The Board reviewed liquidity and capital indicators and requested that management maintain sufficient capacity to absorb adverse changes in credit conditions.

Board Oversight Actions
The Board requested periodic reporting on material changes in portfolio quality, risk concentrations, and credit-loss expectations.

Follow-Up
Management was directed to provide an updated credit-risk dashboard at the next scheduled Board review.
""",

BOARD / "board_credit_risk_memo_2025.txt": """BOARD OVERSIGHT MEMO — FY2025 RISK AND FINANCIAL PERFORMANCE REVIEW
Synthetic test document — non-authoritative.

Purpose
This memo records key matters discussed by the Board concerning financial performance, credit risk, working capital, and risk management.

Financial Performance
Management presented revenue growth, operating expense trends, cash conversion, and working-capital movements.

Credit and Collection Risk
The Board discussed the increase in Accounts Receivable and requested additional monitoring of customer payment behavior and overdue balances.

Risk Appetite
Management confirmed that material risk exposures continued to be evaluated against Board-approved risk appetite limits.

Management Actions
Management committed to strengthening collection monitoring for selected large customer contracts and improving reporting of aging and concentration indicators.

Board Oversight Actions
The Board requested quarterly reporting on receivables aging, customer concentrations, collection performance, and material changes in credit terms.

Follow-Up
Management will report significant deviations from expected collection patterns to the appropriate Board committee.
""",

BOARD / "board_credit_risk_memo_2026.txt": """BOARD OVERSIGHT MEMO — FY2026 CREDIT, LIQUIDITY, AND STRATEGIC OVERSIGHT
Synthetic test document — non-authoritative.

Purpose
This memo summarizes matters considered by the Board during the FY2026 oversight cycle.

Financial and Working-Capital Review
Management reported revenue growth of approximately 12% and a 38% increase in Accounts Receivable. The Board discussed the effect of extended payment terms on cash conversion and working capital.

Credit Risk
The Board reviewed customer concentration, payment behavior, receivables aging, and potential credit deterioration. Management explained that selected large multi-year contracts had payment terms extended from 30 days to 60 days.

Liquidity
The Board requested continued monitoring of cash conversion and liquidity capacity while extended payment terms remain in effect.

Risk Appetite and Controls
Management confirmed that material exposures were being evaluated against established risk appetite and internal control processes.

Board Oversight Actions
The Board requested enhanced reporting on receivables aging, collections, customer concentrations, extended payment terms, and related working-capital effects.

Follow-Up
Management will provide updated metrics and escalation of material adverse trends during subsequent Board reviews.
"""
}

for path, content in documents.items():
    path.write_text(content, encoding="utf-8")

print("CREATED SUCCESSFULLY")
print("=" * 60)

for folder in [MDNA, BOARD]:
    print(f"\n{folder}:")
    for f in sorted(folder.glob("*.txt")):
        print(f"  {f.name} | {len(f.read_text(encoding='utf-8'))} characters")

print("\nTOTAL NEW SOURCE DOCUMENTS:", len(documents))
