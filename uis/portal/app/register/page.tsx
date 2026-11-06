import type { Metadata } from "next";

import { RegisterScreen } from "@/components/RegisterScreen";

export const metadata: Metadata = { title: "Crear cuenta" };

export default async function RegisterPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const params = await searchParams;
  return <RegisterScreen nextRaw={params.next ?? null} />;
}
