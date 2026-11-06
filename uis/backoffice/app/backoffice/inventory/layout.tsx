import { SessionGate } from "@/components/SessionGate";

export default function InventoryLayout({ children }: { children: React.ReactNode }) {
  return <SessionGate>{children}</SessionGate>;
}
