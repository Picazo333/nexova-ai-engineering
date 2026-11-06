import type { Metadata } from "next";

import { ResetPasswordScreen } from "@/components/ResetPasswordScreen";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Restablecer la contraseña",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const params = await searchParams;
  return <ResetPasswordScreen token={params.token ?? ""} />;
}
