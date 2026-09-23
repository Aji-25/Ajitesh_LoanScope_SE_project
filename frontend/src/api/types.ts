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
