from enum import StrEnum


class RoleName(StrEnum):
    ADMIN = "Admin"
    BUSINESS_ANALYST = "Business Analyst"
    STAKEHOLDER = "Stakeholder"
    COMPLIANCE_OFFICER = "Compliance Officer"
    SECURITY_REVIEWER = "Security Reviewer"
    PROJECT_MANAGER = "Project Manager"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class WorkflowStage(StrEnum):
    DISCOVERY = "discovery"
    REQUIREMENTS = "requirements"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    SDLC = "sdlc"
    APPROVAL = "approval"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"
