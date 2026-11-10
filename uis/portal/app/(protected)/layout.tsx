import { SessionGate } from "@/components/SessionGate";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return <SessionGate>{children}</SessionGate>;
}
