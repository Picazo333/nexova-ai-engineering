export type Profile = {
  id: string;
  user_id: string;
  name: string | null;
  phone: string | null;
  address: string | null;
};

export type AuthMe = {
  id: string;
  email: string;
  role: string;
  profile: Profile;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_uuid: string;
};

export type IncidentRule = {
  code: string;
  label_es: string;
  count: number;
};

export type IncidentReport = {
  source_name: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  summary_es: string;
  invalid_breakdown: IncidentRule[];
  categories: { code: string; label_es: string; count: number }[];
};

export type Supplier = {
  id: number;
  name: string;
  country: string;
  categories: string[];
  monthly_rate: number;
  currency: string;
  status: string;
};
