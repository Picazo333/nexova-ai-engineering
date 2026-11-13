import type { Metadata } from "next";

import { LoginScreen } from "@/components/LoginScreen";

export const metadata: Metadata = {
  title: "Entrar · Panel interno",
  description: "Inicio de sesión del panel interno. El token es el JWT de la API de Nexova.",
};

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; reason?: string }>;
}) {
  const params = await searchParams;
  return <LoginScreen nextRaw={params.next ?? null} reason={params.reason ?? null} />;
}
