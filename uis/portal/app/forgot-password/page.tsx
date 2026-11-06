import type { Metadata } from "next";

import { ForgotPasswordScreen } from "@/components/ForgotPasswordScreen";

export const metadata: Metadata = {
  title: "Recuperar la contraseña",
  robots: { index: false, follow: false },
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordScreen />;
}
