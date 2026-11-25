export type User = {
  id: string;
  email: string;
  full_name: string;
  role: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type Project = {
  id: string;
  name: string;
  summary: string;
  product_type: string;
  jurisdiction: string;
  status: string;
  current_stage: string;
  created_at: string;
  updated_at: string;
  stakeholder_count: number;
  requirement_count: number;
  pending_approval_count: number;
};

export type ProjectList = {
  items: Project[];
  total: number;
};

export type ProjectCreate = {
  name: string;
  summary: string;
  product_type: string;
  jurisdiction: string;
  primary_stakeholder?: {
    name: string;
    role: string;
    organization?: string;
  };
};

export type Requirement = {
  id: string;
  project_id: string;
  requirement_code: string;
  statement: string;
  categories: string[];
  source_stakeholder: string;
  priority: string | null;
  assumptions: string[];
  acceptance_criteria: string[];
  confidence: number;
  approval_status: string;
  quality_findings: { kind: string; message: string; question: string }[];
  clarification_status: string;
  version: number;
  created_at: string;
};

export type RequirementCandidate = {
  statement: string;
  categories: string[];
  source: string;
  priority: string | null;
  assumptions: string[];
  acceptance_criteria: string[];
  confidence: number;
  clarification_needed: boolean;
  uncertainty_reason: string | null;
};

export type RequirementExtraction = {
  extraction: { candidates: RequirementCandidate[]; summary: string };
  persisted_requirements: Requirement[];
};

export type RequirementList = { items: Requirement[]; total: number };
export type RequirementWorkflow = { id: string; thread_id: string; status: string; current_node: string; state: { statements?: string[]; clarification_questions?: string[]; clarification_indices?: number[]; iteration?: number; max_iterations?: number; error?: string | null } };

export type KnowledgeDocument = { id: string; filename: string; content_type: string; version: string; jurisdiction: string; effective_date: string | null; status: string; page_count: number; created_at: string };
export type EvidenceChunk = { chunk_id: string; document_id: string; filename: string; content: string; page_number: number | null; section: string | null; version: string; jurisdiction: string; effective_date: string | null; score: number };
export type ComplianceMapping = { id: string; requirement_id: string; obligation: string; applicability: string; rationale: string; evidence_chunk_ids: string[]; citations: { filename: string; section: string | null; page: number | null; version: string; jurisdiction: string }[]; confidence: number; status: string; gap_status: string; human_review_required: boolean; created_at: string };
export type SecurityFinding = { id: string; requirement_id: string; category: string; title: string; description: string; severity: string; recommendation: string; status: string; created_at: string };
export type Risk = { id: string; requirement_id: string | null; risk_code: string; category: string; description: string; likelihood: number; impact: number; score: number; mitigation: string; owner_role: string; status: string; created_at: string };
export type Approval = { id: string; entity_type: string; entity_id: string | null; title: string; assigned_role: string; status: string; decision_comment: string | null; workflow_thread_id: string | null; request_payload: Record<string, unknown>; decision_payload: Record<string, unknown>; created_at: string; decided_at: string | null };
export type SDLCRecommendation = { id: string; characteristics: Record<string, number>; scores: Record<string, number>; recommendation: string; rationale: string; scoring_version: string; approval_status: string; created_at: string };
export type Artifact = { id: string; artifact_type: string; title: string; version: number; content: Record<string, unknown>; source_requirement_ids: string[]; created_at: string };
export type Evaluation = { id: string; metrics: Record<string, number>; passed: boolean; summary: string; created_at: string };
export type AuditEvent = { id: string; actor_type: string; actor_id: string | null; agent_name: string | null; action: string; entity_type: string; entity_id: string | null; event_metadata: Record<string, unknown>; created_at: string };
