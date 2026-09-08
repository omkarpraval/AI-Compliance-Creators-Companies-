/**
 * AUTOMATICALLY GENERATED FROM VERIFYD OPENAPI SPECIFICATION
 * DO NOT EDIT MANUALLY
 */

export interface User {
  id: string;
  org_id?: string | null;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  role: 'company_admin' | 'company_member' | 'creator' | 'platform_admin';
  is_active: boolean;
  last_login_at?: string | null;
  created_at: string;
  updated_at: string;
  handle?: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Organization {
  id: string;
  name: string;
  type: 'brand' | 'agency';
  logo_url?: string | null;
  country: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: string;
  org_id: string;
  name: string;
  product_name: string;
  description?: string | null;
  starts_on?: string | null;
  ends_on?: string | null;
  status: 'draft' | 'active' | 'closed';
  created_by?: string | null;
  created_at: string;
  updated_at: string;
  contract_count?: number;
  submission_count?: number;
}

export type ClauseType =
  | 'min_spoken_duration'
  | 'required_phrase'
  | 'prohibited_mention'
  | 'visual_presence'
  | 'visual_timing'
  | 'disclosure_tag'
  | 'tone_requirement'
  | 'manual_only';

export type Modality = 'audio' | 'visual' | 'text_overlay' | 'metadata' | 'mixed';
export type Severity = 'critical' | 'standard' | 'advisory';
export type ReviewStatus = 'unreviewed' | 'confirmed' | 'edited' | 'rejected';
export type Verdict = 'pass' | 'fail' | 'flagged';

export interface Clause {
  id: string;
  contract_id: string;
  ordinal: number;
  clause_ref: string;
  source_text: string;
  requirement: string;
  clause_type: ClauseType;
  params: Record<string, any>;
  modality: Modality;
  severity: Severity;
  is_auto_checkable: boolean;
  confidence: number;
  review_status: ReviewStatus;
  edited_by?: string | null;
  edited_at?: string | null;
  source_page?: number | null;
  source_bbox?: {
    page: number;
    x0: number;
    top: number;
    x1: number;
    bottom: number;
  } | null;
  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: string;
  campaign_id: string;
  creator_id: string;
  version: number;
  parent_contract_id?: string | null;
  source_file_key?: string | null;
  raw_document_key?: string | null;
  source_content_hash?: string | null;
  status: 'draft' | 'extracting' | 'needs_review' | 'sent' | 'signed' | 'superseded';
  esign_envelope_id?: string | null;
  signed_at?: string | null;
  fee_amount?: number | null;
  fee_currency: string;
  created_at: string;
  updated_at: string;
  campaign_name?: string | null;
  creator_name?: string | null;
  creator_handle?: string | null;
  clauses?: Clause[];
}

export interface ExtractedWord {
  text: string;
  page: number;
  x0: number;
  top: number;
  x1: number;
  bottom: number;
}

export interface ExtractedPage {
  page: number;
  width: number;
  height: number;
  text: string;
  words: ExtractedWord[];
  has_text_layer: boolean;
}

export interface ExtractedDocument {
  page_count: number;
  full_text: string;
  pages: ExtractedPage[];
  is_scanned: boolean;
  extraction_method: string;
  content_hash: string;
  char_count: number;
}

export interface EvidenceItem {
  id: string;
  clause_verdict_id: string;
  type: 'transcript_span' | 'visual_detection' | 'ocr_text' | 'caption_span';
  start_ms: number;
  end_ms: number;
  payload: {
    text?: string;
    bbox?: { x: number; y: number; w: number; h: number };
    label?: string;
    confidence?: number;
    [key: string]: any;
  };
  thumbnail_key?: string | null;
  created_at: string;
}

export interface ClauseVerdict {
  id: string;
  report_id: string;
  clause_id: string;
  clause_ref: string;
  verdict: Verdict;
  confidence: number;
  rationale: string;
  measured_value: Record<string, any>;
  required_value: Record<string, any>;
  is_overridden: boolean;
  override_verdict?: Verdict | null;
  override_reason?: string | null;
  overridden_by?: string | null;
  overridden_at?: string | null;
  evidence_items: EvidenceItem[];
}

export interface ComplianceReport {
  id: string;
  submission_id: string;
  overall_score: number;
  verdict: 'pass' | 'fail' | 'needs_review';
  clauses_total: number;
  clauses_passed: number;
  clauses_failed: number;
  clauses_flagged: number;
  model_version: string;
  prompt_version: string;
  generated_at: string;
  processing_ms: number;
  cost_estimate_usd: number;
  verdicts: ClauseVerdict[];
}

export interface Submission {
  id: string;
  contract_id: string;
  contract_version: number;
  creator_id: string;
  kind: 'preflight' | 'final';
  video_file_key: string;
  duration_seconds?: number | null;
  caption_text?: string | null;
  platform_url?: string | null;
  status:
    | 'draft'
    | 'uploaded'
    | 'queued'
    | 'processing'
    | 'report_ready'
    | 'in_review'
    | 'approved'
    | 'rejected'
    | 'changes_requested'
    | 'failed';
  submitted_at?: string | null;
  attempt_number: number;
  created_at: string;
  updated_at: string;
  campaign_name?: string | null;
  creator_name?: string | null;
  creator_handle?: string | null;
  product_name?: string | null;
  report?: ComplianceReport | null;
}

export interface SubmissionStatus {
  submission_id: string;
  status: string;
  progress: number;
  stage: string;
  error_message?: string | null;
}

export interface CreatorProfile {
  id: string;
  user_id: string;
  handle: string;
  bio?: string | null;
  primary_language: string;
  niches: string[];
  is_verified: boolean;
  public_id_enabled: boolean;
  full_name?: string | null;
  avatar_url?: string | null;
}

export interface CreatorID {
  handle: string;
  full_name: string;
  bio?: string | null;
  avatar_url?: string | null;
  is_verified: boolean;
  pass_rate: number;
  campaigns_completed: number;
  average_revisions: number;
  total_submissions: number;
  public_id_enabled: boolean;
  niches: string[];
  primary_language: string;
}

export interface ClauseDiffItem {
  change_type: 'added' | 'removed' | 'modified' | 'unchanged';
  clause_ref: string;
  current_clause?: Clause | null;
  previous_clause?: Clause | null;
  diff_fields?: string[] | null;
}

export interface ContractDiff {
  base_contract_id: string;
  base_version: number;
  target_contract_id: string;
  target_version: number;
  summary: string;
  diff_items: ClauseDiffItem[];
}

export interface Job {
  id: string;
  submission_id?: string | null;
  task_name: string;
  celery_task_id?: string | null;
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'retrying';
  attempt: number;
  max_attempts: number;
  error_class?: string | null;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  created_at: string;
}

export interface AdminMetrics {
  total_submissions: number;
  passed_count: number;
  failed_count: number;
  flagged_count: number;
  pass_rate: number;
  avg_processing_ms: number;
  total_api_spend_usd: number;
  spend_by_provider: Record<string, number>;
  jobs_by_status: Record<string, number>;
  avg_turnaround_hours: number;
}

export interface AuditEvent {
  id: string;
  actor_id?: string | null;
  actor_type: string;
  entity_type: string;
  entity_id: string;
  action: string;
  before?: Record<string, any> | null;
  after?: Record<string, any> | null;
  ip_address?: string | null;
  created_at: string;
  actor_name?: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  next_cursor?: string | null;
  total?: number | null;
}

export interface ErrorEnvelope {
  error: {
    code: string;
    message: string;
    details: Record<string, any>;
    request_id: string;
  };
}
