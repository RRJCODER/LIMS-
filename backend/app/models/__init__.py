# Import all models so Alembic can auto-detect them for migrations
from app.models.audit import AuditLog, AuditAction
from app.models.user import User, UserQualification, TrainingRecord, Role
from app.models.specification import ProductQualityGrade, AnalyteSpecification
from app.models.method import AnalyticalMethod, MethodVersion, Analyte, MethodStatus
from app.models.sample import Sample, SampleCustody, SampleAttachment, SampleStatus, SampleMatrix
from app.models.test import TestRequest, TestResult, TestStatus
from app.models.qc import QCBatch, QCResult, ControlChart, WestgardViolation, QCType, WestgardRule
from app.models.equipment import Equipment, CalibrationRecord, MaintenanceLog, EquipmentStatus
from app.models.document import Document, DocumentVersion, ApprovalRecord, DocumentType, DocumentStatus
from app.models.instrument_data import RawInstrumentReading, GCImport
from app.models.report import CertificateOfAnalysis, ReportTemplate

__all__ = [
    "AuditLog", "AuditAction",
    "User", "UserQualification", "TrainingRecord", "Role",
    "ProductQualityGrade", "AnalyteSpecification",
    "AnalyticalMethod", "MethodVersion", "Analyte", "MethodStatus",
    "Sample", "SampleCustody", "SampleAttachment", "SampleStatus", "SampleMatrix",
    "TestRequest", "TestResult", "TestStatus",
    "QCBatch", "QCResult", "ControlChart", "WestgardViolation", "QCType", "WestgardRule",
    "Equipment", "CalibrationRecord", "MaintenanceLog", "EquipmentStatus",
    "Document", "DocumentVersion", "ApprovalRecord", "DocumentType", "DocumentStatus",
    "RawInstrumentReading", "GCImport",
    "CertificateOfAnalysis", "ReportTemplate",
]
