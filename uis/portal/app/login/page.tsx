import type { Metadata } from "next";

import { LoginScreen } from "@/components/LoginScreen";

export const metadata: Metadata = { title: "Entrar" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; reason?: string; notice?: string }>;
}) {
  const params = await searchParams;
  return (
    <LoginScreen
      nextRaw={params.next ?? null}
      reason={params.reason ?? null}
      notice={params.notice ?? null}
    />
  );
}
