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
