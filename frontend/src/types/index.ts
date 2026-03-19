export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  tenant_id: string;
  roles: string[];
}

export interface Role {
  id: string;
  name: string;
  description: string | null;
  is_system: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Company {
  id: string;
  tenant_id: string;
  name: string;
  legal_form: string | null;
  ice: string | null;
  if_number: string | null;
  rc: string | null;
}

export interface Dossier {
  id: string;
  tenant_id: string;
  company_id: string;
  name: string;
  status: string;
}

export interface FiscalYear {
  id: string;
  dossier_id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface AccountingPeriod {
  id: string;
  fiscal_year_id: string;
  name: string;
  start_date: string;
  end_date: string;
  period_number: number;
  status: string;
}

export interface Account {
  id: string;
  dossier_id: string;
  number: string;
  label: string;
  account_class: number;
  account_type: string;
  nature: string;
  is_system: boolean;
  is_lettrable: boolean;
  default_tva_rate: string | null;
  parent_number: string | null;
}

export interface Journal {
  id: string;
  dossier_id: string;
  code: string;
  label: string;
  journal_type: string;
}

export interface EntryLine {
  id: string;
  line_number: number;
  account_id: string;
  label: string;
  debit: string;
  credit: string;
  third_party_id: string | null;
  lettrage_code: string | null;
  account_number: string | null;
  account_label: string | null;
}

export interface DashboardStats {
  accounts_count: number;
  journals_count: number;
  entries_count: number;
  draft_entries_count: number;
  validated_entries_count: number;
  fiscal_years_count: number;
  open_fiscal_years_count: number;
  periods_count: number;
  open_periods_count: number;
  locked_periods_count: number;
  third_parties_count: number;
  total_debit: string;
  total_credit: string;
}

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  created_at: string;
}

export interface JournalEntry {
  id: string;
  dossier_id: string;
  journal_id: string;
  period_id: string;
  entry_date: string;
  piece_number: string;
  label: string;
  status: string;
  reference: string | null;
  reversal_of_id: string | null;
  lines: EntryLine[];
  total_debit: string;
  total_credit: string;
}
