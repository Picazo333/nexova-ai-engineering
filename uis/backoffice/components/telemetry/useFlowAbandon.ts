"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

import { abandonFlow, armFlow, cancelFlow } from "@/lib/telemetry-catalog";

export type FlowName = "inventory_inbound" | "inventory_outbound" | "login";

export function useFlowAbandon(flow: FlowName, dirty: boolean, lastField: string): () => void {
  const pathname = usePathname();
  const dirtyRef = useRef(dirty);
  const fieldRef = useRef(lastField);
  const succeededRef = useRef(false);
  const startedRef = useRef<number | null>(null);
  dirtyRef.current = dirty;
  fieldRef.current = lastField;

  useEffect(() => {
    if (succeededRef.current) return;
    if (dirty && startedRef.current == null) {
      startedRef.current = Date.now();
      armFlow(flow);
    }
    if (!dirty) {
      startedRef.current = null;
      cancelFlow(flow);
    }
  }, [dirty, flow]);

  useEffect(() => {
    let hiddenTimer: number | undefined;
    let sent = false;
    function emit() {
      if (sent || !dirtyRef.current || succeededRef.current || startedRef.current == null) return;
      sent = true;
      abandonFlow(flow, Date.now() - startedRef.current, fieldRef.current);
    }
    function onVisibility() {
      if (document.visibilityState === "hidden") {
        hiddenTimer = window.setTimeout(emit, 60_000);
      } else if (hiddenTimer) {
        window.clearTimeout(hiddenTimer);
        hiddenTimer = undefined;
      }
    }
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      if (hiddenTimer) window.clearTimeout(hiddenTimer);
      emit();
    };
  }, [flow, pathname]);

  return () => {
    succeededRef.current = true;
    cancelFlow(flow);
    startedRef.current = null;
  };
}
