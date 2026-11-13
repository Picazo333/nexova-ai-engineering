import { apiFetch } from "@/lib/http";

export type AuthMe = {
  id: string;
  email: string;
  role: string;
  profile: { id: string; user_id: string; name: string | null };
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_uuid: string;
};

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
    { auth: false },
  );
}

export function fetchMe(): Promise<AuthMe> {
  return apiFetch<AuthMe>("/auth/me");
}
