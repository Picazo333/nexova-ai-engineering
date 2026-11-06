import type { Metadata } from "next";

import { ChangePasswordScreen } from "@/components/ChangePasswordScreen";

export const metadata: Metadata = {
  title: "Cambiar la contraseña",
  robots: { index: false, follow: false },
};

export default function ChangePasswordPage() {
  return <ChangePasswordScreen />;
}
