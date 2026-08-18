import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    """Local development identity used by the dashboard sign-in flow."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False, default="Audit Manager")
    password_hash = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)


class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    client_name = Column(String(255), nullable=False, default="Apex Global Technologies Inc.")
    period_ending = Column(String(50), nullable=False, default="2025-12-31")
    framework = Column(String(50), nullable=False, default="US GAAP / IFRS")
    review_stage = Column(String(50), nullable=False, default="CY_DRAFT_FS")
    risk_status = Column(String(50), nullable=False, default="CLEAN")  # CLEAN, CORRECTED, WAIVED_RISK, REVIEW_REQUIRED
    r2_raw_folder_key = Column(String(512), nullable=True)
    
    overall_materiality = Column(Float, default=440000.0)
    performance_materiality = Column(Float, default=330000.0)
    trivial_threshold = Column(Float, default=22000.0)
    
    total_procedures = Column(Integer, default=56)
    passed_procedures = Column(Integer, default=0)
    flagged_procedures = Column(Integer, default=0)
    failed_procedures = Column(Integer, default=0)
    
    raw_payload = Column(JSON, nullable=True)
    corrected_payload = Column(JSON, nullable=True)
    summary_report = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    rule_results = relationship("AuditRuleResult", back_populates="engagement", cascade="all, delete-orphan")
    waiver_records = relationship("AuditWaiverLedger", back_populates="engagement", cascade="all, delete-orphan")
    artifacts = relationship("ReportArtifact", back_populates="engagement", cascade="all, delete-orphan")


class AuditRuleResult(Base):
    __tablename__ = "audit_rule_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    rule_id = Column(String(100), nullable=False)
    category = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)  # Critical, High, Medium, Low
    status = Column(String(50), nullable=False)  # PASS, FLAGGED, FAIL
    submitted_value = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    variance_amount = Column(Float, nullable=True)
    variance_pct = Column(Float, nullable=True)
    qdrant_vector_id = Column(String(100), nullable=True)
    resolution_status = Column(String(50), default="UNRESOLVED")  # UNRESOLVED, ACCEPTED, WAIVED
    audit_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    engagement = relationship("Engagement", back_populates="rule_results")


class AuditWaiverLedger(Base):
    __tablename__ = "audit_waiver_ledger"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    rule_id = Column(String(100), nullable=False)
    user_decision = Column(String(50), nullable=False)  # ACCEPTED, WAIVED
    justification_notes = Column(Text, nullable=True)
    resolved_by = Column(String(100), default="Audit Manager")
    submitted_value = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    adjustment_applied = Column(JSON, nullable=True)
    resolved_at = Column(DateTime, default=datetime.datetime.utcnow)

    engagement = relationship("Engagement", back_populates="waiver_records")


class ReportArtifact(Base):
    __tablename__ = "report_artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # PDF_WP514, CORRECTED_XLSX, JSON_PAYLOAD, AUDIT_TRAIL_ZIP
    file_name = Column(String(255), nullable=False)
    r2_object_key = Column(String(512), nullable=True)
    file_path = Column(String(512), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    engagement = relationship("Engagement", back_populates="artifacts")


class DashboardMetric(Base):
    __tablename__ = "dashboard_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True, default="neutral")
    period = Column(String(50), nullable=False, default="2025-12-31")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    engagement = relationship("Engagement")


class DashboardFinding(Base):
    __tablename__ = "dashboard_findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    rule_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(150), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="OPEN")
    owner = Column(String(150), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    engagement = relationship("Engagement")


class DashboardActivity(Base):
    __tablename__ = "dashboard_activity"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    user_name = Column(String(150), nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    engagement = relationship("Engagement")


class DashboardSavedView(Base):
    __tablename__ = "dashboard_saved_views"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    engagement_id = Column(String(36), ForeignKey("engagements.id"), nullable=False)
    user_id = Column(String(36), nullable=True)
    view_name = Column(String(150), nullable=False)
    filters_json = Column(JSON, nullable=True)
    layout_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    engagement = relationship("Engagement")
