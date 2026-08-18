# math_engine/schemas.py
from enum import Enum
from typing import Optional, List, Union, Any, Dict
from pydantic import BaseModel, Field, model_validator


# ==============================================================================
# 1. ENUMS & METADATA SCHEMAS
# ==============================================================================

class DocumentType(str, Enum):
    CY_DRAFT_FS = "CY_DRAFT_FS"
    PY_AUDITED_FS = "PY_AUDITED_FS"


class ExtractionEngine(str, Enum):
    PYMUPDF = "PYMUPDF"
    CAMELOT = "CAMELOT"
    VISION_LLM = "VISION_LLM"


class Metadata(BaseModel):
    """Metadata regarding entity, reporting period, and document ingestion."""
    client_name: Optional[str] = Field(default="Apex Global Technologies Inc.", description="Legal company/entity name being audited")
    period: Optional[str] = Field(default="2025-12-31", description="Current reporting period end date")
    currency: Optional[str] = Field(default="USD", description="Reporting currency")
    scale: Optional[str] = Field(default="EXACT", description="Reporting scale")
    framework: Optional[str] = Field(default="US GAAP / IFRS", description="Accounting framework")
    review_stage: Optional[str] = Field(default="CY_DRAFT_FS", description="Review stage")
    entity_name: Optional[str] = Field(default=None, description="Legal company/entity name being audited")
    period_end_date: Optional[str] = Field(default=None, description="Current reporting period end date (YYYY-MM-DD)")
    comparative_period_end_date: Optional[str] = Field(default=None, description="Comparative prior period end date (YYYY-MM-DD)")
    document_type: Optional[DocumentType] = Field(default=DocumentType.CY_DRAFT_FS, description="Type of document")
    extraction_engine: Optional[ExtractionEngine] = Field(default=ExtractionEngine.VISION_LLM, description="Ingestion engine used")

    @model_validator(mode="before")
    @classmethod
    def populate_defaults(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "client_name" in values and not values.get("entity_name"):
                values["entity_name"] = values["client_name"]
            elif "entity_name" in values and not values.get("client_name"):
                values["client_name"] = values["entity_name"]

            if "period" in values and not values.get("period_end_date"):
                values["period_end_date"] = values["period"]
            elif "period_end_date" in values and not values.get("period"):
                values["period"] = values["period_end_date"]
        return values


ReportMetadata = Metadata


# ==============================================================================
# 2. FINANCIAL STATEMENT VALUE DEFINITIONS
# ==============================================================================

class BalanceSheetValues(BaseModel):
    """Line items for Balance Sheet."""
    cash_and_cash_equivalents: Optional[float] = 0.0
    accounts_receivable_net: Optional[float] = 0.0
    inventory: Optional[float] = 0.0
    prepaid_expenses: Optional[float] = 0.0
    total_current_assets: Optional[float] = 0.0
    ppe_net: Optional[float] = 0.0
    intangible_assets: Optional[float] = 0.0
    total_non_current_assets: Optional[float] = 0.0
    total_assets: float = Field(..., description="Total Assets (Required)")
    accounts_payable: Optional[float] = 0.0
    accrued_expenses: Optional[float] = 0.0
    short_term_debt: Optional[float] = 0.0
    current_portion_of_lt_debt: Optional[float] = 0.0
    total_current_liabilities: Optional[float] = 0.0
    long_term_debt: Optional[float] = 0.0
    total_non_current_liabilities: Optional[float] = 0.0
    total_liabilities: float = Field(..., description="Total Liabilities (Required)")
    common_stock: Optional[float] = 0.0
    additional_paid_in_capital: Optional[float] = 0.0
    retained_earnings: Optional[float] = 0.0
    aoci: Optional[float] = 0.0
    treasury_stock: Optional[float] = 0.0
    total_equity: float = Field(..., description="Total Equity (Required)")


class IncomeStatementValues(BaseModel):
    """Line items for Income Statement."""
    revenue: float = Field(..., description="Revenue (Required)")
    cogs: float = Field(..., description="Cost of Goods Sold (Required)")
    gross_profit: float = Field(..., description="Gross Profit (Required)")
    sga_expense: Optional[float] = 0.0
    rd_expense: Optional[float] = 0.0
    depreciation_amortization: Optional[float] = 0.0
    total_operating_expenses: float = Field(..., description="Total OpEx (Required)")
    operating_income: float = Field(..., description="Operating Income (Required)")
    interest_expense: Optional[float] = 0.0
    non_operating_income: Optional[float] = 0.0
    income_tax_expense: Optional[float] = 0.0
    net_income: float = Field(..., description="Net Income (Required)")


class CashFlowValues(BaseModel):
    """Line items for Cash Flow Statement."""
    net_income_starting: float = Field(..., description="Net Income Starting (Required)")
    depreciation_addback: Optional[float] = 0.0
    working_capital_changes: Optional[float] = 0.0
    operating_cash_flow: float = Field(..., description="Operating CF (Required)")
    capital_expenditures: Optional[float] = 0.0
    investing_cash_flow: float = Field(..., description="Investing CF (Required)")
    debt_repayments_or_borrowings: Optional[float] = 0.0
    dividends_paid: Optional[float] = 0.0
    financing_cash_flow: float = Field(..., description="Financing CF (Required)")
    net_cash_change: float = Field(..., description="Net Cash Change (Required)")
    beginning_cash: float = Field(..., description="Beginning Cash (Required)")
    ending_cash: float = Field(..., description="Ending Cash (Required)")


# ==============================================================================
# 3. STATEMENTS & SCHEDULES CONTAINERS
# ==============================================================================

class BalanceSheetPeriod(BaseModel):
    current_period: BalanceSheetValues
    prior_period: BalanceSheetValues


class IncomeStatementPeriod(BaseModel):
    current_period: IncomeStatementValues
    prior_period: IncomeStatementValues


class CashFlowStatementPeriod(BaseModel):
    current_period: CashFlowValues
    prior_period: CashFlowValues


class StockholdersEquity(BaseModel):
    beginning_retained_earnings: Optional[float] = 0.0
    net_income: Optional[float] = 0.0
    dividends_declared: Optional[float] = 0.0
    ending_retained_earnings: Optional[float] = 0.0


class Statements(BaseModel):
    """Main financial statements container."""
    balance_sheet: BalanceSheetPeriod
    income_statement: IncomeStatementPeriod
    cash_flow_statement: CashFlowStatementPeriod
    stockholders_equity: Optional[StockholdersEquity] = None


class AccountsReceivableAging(BaseModel):
    current: Optional[float] = 0.0
    days_1_30: Optional[float] = 0.0
    days_31_60: Optional[float] = 0.0
    days_61_90: Optional[float] = 0.0
    days_over_90: Optional[float] = 0.0
    gross_ar: Optional[float] = 0.0
    allowance_for_credit_losses: Optional[float] = 0.0
    net_ar: Optional[float] = 0.0


class PPESchedule(BaseModel):
    gross_ppe: Optional[float] = 0.0
    accumulated_depreciation: Optional[float] = 0.0
    net_ppe: Optional[float] = 0.0
    additions_capex: Optional[float] = 0.0
    disposals: Optional[float] = 0.0
    depreciation_expense: Optional[float] = 0.0


class DebtMaturities(BaseModel):
    year_1: Optional[float] = 0.0
    year_2: Optional[float] = 0.0
    year_3: Optional[float] = 0.0
    year_4: Optional[float] = 0.0
    year_5: Optional[float] = 0.0
    thereafter: Optional[float] = 0.0
    total_debt: Optional[float] = 0.0


class Schedules(BaseModel):
    """Supplementary schedules container for legacy compatibility."""
    accounts_receivable_aging: Optional[AccountsReceivableAging] = None
    ppe_schedule: Optional[PPESchedule] = None
    debt_maturities: Optional[DebtMaturities] = None


class Footnotes(BaseModel):
    """Footnotes & supplementary schedules container."""
    ar_aging: Optional[AccountsReceivableAging] = Field(default=None, description="Accounts Receivable Aging schedule")
    ppe_sched: Optional[PPESchedule] = Field(default=None, description="PP&E Roll-forward schedule")
    debt_maturity: Optional[DebtMaturities] = Field(default=None, description="Debt Maturity schedule")


class PriorData(BaseModel):
    """Prior period financial data container."""
    balance_sheet: BalanceSheetValues = Field(..., description="Audited Prior-Year Balance Sheet")
    income_statement: IncomeStatementValues = Field(..., description="Audited Prior-Year Income Statement")
    final_trial_balance: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Final Trial Balance Excel/JSON data")


class CurrentData(BaseModel):
    """Current period financial data container."""
    preliminary_trial_balance: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Preliminary Trial Balance Excel/JSON data")
    balance_sheet: BalanceSheetValues = Field(..., description="Preliminary Current-Year Balance Sheet")
    income_statement: IncomeStatementValues = Field(..., description="Preliminary Current-Year Income Statement")
    cash_flow_statement: CashFlowValues = Field(..., description="Preliminary Current-Year Cash Flow Statement")
    equity_statement: Optional[StockholdersEquity] = Field(default=None, description="Statement of Stockholders Equity")
    footnotes: Optional[Footnotes] = Field(default_factory=Footnotes, description="Footnotes & Supplementary Schedules")


class YoYVariance(BaseModel):
    rule_id: Optional[str] = "ANALYTICS_01"
    line_item: str
    current_year: float
    prior_year: float
    dollar_change: float
    pct_change: Optional[float] = 0.0
    pct_change_raw: Optional[float] = 0.0
    pct_change_formatted: str
    audit_action: str
    commentary: Optional[str] = ""


class CommonSizeItem(BaseModel):
    rule_id: Optional[str] = "ANALYTICS_03"
    statement: Optional[str] = ""
    line_item: str
    amount: float
    base_amount: Optional[float] = 0.0
    pct_of_base: float
    pct_formatted: Optional[str] = ""
    formatted_pct: Optional[str] = ""


class RatioResult(BaseModel):
    rule_id: str
    category: str
    ratio_name: str
    formula: str
    value: float
    formatted_value: str
    benchmark: str
    status: str
    assessment: Optional[str] = ""


class DisconnectResult(BaseModel):
    rule_id: str
    rule_name: str
    metric_value: float
    threshold: float
    status: str
    audit_implication: Optional[str] = ""
    description: Optional[str] = None


class AuditFlag(BaseModel):
    rule_id: str
    category: str
    description: str
    source_ref: Optional[str] = "N/A"
    expected: float
    actual: float
    difference: Optional[float] = 0.0
    status: Optional[str] = "PASS"
    severity: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def calc_diff_and_status(cls, values: Any) -> Any:
        if isinstance(values, dict):
            exp = float(values.get("expected", 0.0) or 0.0)
            act = float(values.get("actual", 0.0) or 0.0)
            diff = round(abs(act - exp), 2)
            values["difference"] = diff
            if "status" not in values or not values["status"]:
                values["status"] = "PASS" if diff <= 0.01 else "FAIL"
        return values


class GuardrailResult(BaseModel):
    rule_id: str
    category: str
    rule_name: str
    status: str
    message: str
    value: float
    benchmark: str


class FinancialReportInput(BaseModel):
    metadata: Metadata
    statements: Optional[Statements] = None
    schedules: Optional[Schedules] = None


class AnalysisSummary(BaseModel):
    open_exceptions_count: int = 0


# ==============================================================================
# 4. ROOT INGESTION SCHEMA
# ==============================================================================

class FinancialStatementsIngestionSchema(BaseModel):
    """Root JSON schema for financial statement ingestion matching expected folder structure."""
    metadata: Metadata
    prior_data: PriorData
    current_data: CurrentData

    # Legacy fields for backward compatibility
    statements: Optional[Statements] = None
    schedules: Optional[Schedules] = None

    @model_validator(mode="before")
    @classmethod
    def convert_nested_structure(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # If current_data and prior_data are passed, populate statements and schedules
            if "current_data" in values and "prior_data" in values:
                curr = values["current_data"]
                prior = values["prior_data"]
                
                curr_bs = curr.get("balance_sheet") or curr.get("bs")
                prior_bs = prior.get("balance_sheet") or prior.get("bs")
                
                curr_is = curr.get("income_statement") or curr.get("inc")
                prior_is = prior.get("income_statement") or prior.get("inc")

                curr_cf = curr.get("cash_flow_statement") or curr.get("cf")
                prior_cf = prior.get("cash_flow_statement") or prior.get("cf") or curr_cf

                equity = curr.get("equity_statement") or curr.get("stockholders_equity")
                fn = curr.get("footnotes") or curr.get("schedules") or {}

                values["statements"] = {
                    "balance_sheet": {"current_period": curr_bs, "prior_period": prior_bs},
                    "income_statement": {"current_period": curr_is, "prior_period": prior_is},
                    "cash_flow_statement": {"current_period": curr_cf, "prior_period": prior_cf},
                    "stockholders_equity": equity
                }

                values["schedules"] = {
                    "accounts_receivable_aging": fn.get("ar_aging") or fn.get("accounts_receivable_aging"),
                    "ppe_schedule": fn.get("ppe_sched") or fn.get("ppe_schedule"),
                    "debt_maturities": fn.get("debt_maturity") or fn.get("debt_maturities")
                }

            # If legacy statements & schedules are passed, populate current_data and prior_data
            elif "statements" in values:
                stmts = values["statements"]
                scheds = values.get("schedules", {})

                bs = stmts.get("balance_sheet", {})
                is_st = stmts.get("income_statement", {})
                cf = stmts.get("cash_flow_statement", {})
                eq = stmts.get("stockholders_equity")

                values["prior_data"] = {
                    "balance_sheet": bs.get("prior_period"),
                    "income_statement": is_st.get("prior_period"),
                    "final_trial_balance": {}
                }

                values["current_data"] = {
                    "preliminary_trial_balance": {},
                    "balance_sheet": bs.get("current_period"),
                    "income_statement": is_st.get("current_period"),
                    "cash_flow_statement": cf.get("current_period"),
                    "equity_statement": eq,
                    "footnotes": {
                        "ar_aging": scheds.get("accounts_receivable_aging"),
                        "ppe_sched": scheds.get("ppe_schedule"),
                        "debt_maturity": scheds.get("debt_maturities")
                    }
                }
        return values

    @property
    def balance_sheet(self) -> BalanceSheetValues:
        if self.current_data and self.current_data.balance_sheet:
            return self.current_data.balance_sheet
        return self.statements.balance_sheet.current_period

    @property
    def income_statement(self) -> IncomeStatementValues:
        if self.current_data and self.current_data.income_statement:
            return self.current_data.income_statement
        return self.statements.income_statement.current_period

    @property
    def cash_flow_statement(self) -> CashFlowValues:
        if self.current_data and self.current_data.cash_flow_statement:
            return self.current_data.cash_flow_statement
        return self.statements.cash_flow_statement.current_period

    @property
    def note_3_ar_aging(self) -> Optional[AccountsReceivableAging]:
        if self.current_data and self.current_data.footnotes and self.current_data.footnotes.ar_aging:
            return self.current_data.footnotes.ar_aging
        return self.schedules.accounts_receivable_aging if self.schedules else None

    @property
    def note_4_ppe_schedule(self) -> Optional[PPESchedule]:
        if self.current_data and self.current_data.footnotes and self.current_data.footnotes.ppe_sched:
            return self.current_data.footnotes.ppe_sched
        return self.schedules.ppe_schedule if self.schedules else None

    @property
    def note_7_debt_schedule(self) -> Optional[DebtMaturities]:
        if self.current_data and self.current_data.footnotes and self.current_data.footnotes.debt_maturity:
            return self.current_data.footnotes.debt_maturity
        return self.schedules.debt_maturities if self.schedules else None

    @property
    def prior_year_audited_database(self) -> BalanceSheetValues:
        if self.prior_data and self.prior_data.balance_sheet:
            return self.prior_data.balance_sheet
        return self.statements.balance_sheet.prior_period

    @property
    def prior_year_income_statement(self) -> IncomeStatementValues:
        if self.prior_data and self.prior_data.income_statement:
            return self.prior_data.income_statement
        return self.statements.income_statement.prior_period

    @property
    def comparative_prior_year_in_current_report(self) -> IncomeStatementValues:
        return self.prior_year_income_statement
