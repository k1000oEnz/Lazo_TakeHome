export type Status = "pending" | "in_progress" | "submitted" | "done";

export type ObligationType =
  | "annual_report"
  | "franchise_tax"
  | "boi_report"
  | "registered_agent_renewal";

export interface Obligation {
  id: string;
  type: ObligationType;
  title: string;
  description: string | null;
  due_date: string;
  owner: string;
  requires_document: boolean;
  status: Status;
  company_tax_id: string;
  is_overdue: boolean;
  tax_id_masked: string;
  version: number;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  size: number;
  uploaded_at: string;
}

export interface HistoryEntry {
  id: string;
  from_status: Status;
  to_status: Status;
  at: string;
  actor: string | null;
}

export interface ObligationDetail extends Obligation {
  documents: DocumentSummary[];
  history: HistoryEntry[];
  available_transitions: Status[];
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ObligationCreateInput {
  type: ObligationType;
  title: string;
  description?: string | null;
  due_date: string;
  owner: string;
  requires_document: boolean;
  company_tax_id: string;
}

export interface ObligationUpdateInput {
  title?: string;
  description?: string | null;
  due_date?: string;
  owner?: string;
  requires_document?: boolean;
}

export interface TransitionInput {
  to_status: Status;
  version: number;
  document_id?: string;
  actor?: string;
}
