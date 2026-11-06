"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { AppHeader } from "@/components/AppHeader";
import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { ApiError, apiFetch } from "@/lib/api";
import { readToken } from "@/lib/session";
import type { AuthMe } from "@/lib/types";

type Phase =
  | { kind: "checking" }
  | { kind: "in"; me: AuthMe }
  | { kind: "offline"; message: string };

type SessionValue = {
  phase: Phase;
  retry: () => void;
  refresh: () => Promise<void>;
};

const SessionContext = createContext<SessionValue | null>(null);

export function useSession(): SessionValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession fuera del guard");
  return value;
}

export function SessionGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const pathRef = useRef(pathname);
  pathRef.current = pathname;
  const [phase, setPhase] = useState<Phase>({ kind: "checking" });
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => setAttempt((value) => value + 1), []);

  useEffect(() => {
    let cancelled = false;
    if (!readToken()) {
      const next = encodeURIComponent(pathRef.current || "/");
      router.replace(`/login?next=${next}`);
      return () => {
        cancelled = true;
      };
    }
    setPhase({ kind: "checking" });
    apiFetch<AuthMe>("/auth/me")
      .then((me) => {
        if (!cancelled) setPhase({ kind: "in", me });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 401) return;
        const message =
          error instanceof ApiError
            ? error.message
            : "No hay conexión con la API para comprobar la sesión.";
        setPhase({ kind: "offline", message });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, router]);

  const refresh = useCallback(async () => {
    try {
      const me = await apiFetch<AuthMe>("/auth/me");
      setPhase({ kind: "in", me });
    } catch (error: unknown) {
      if (error instanceof ApiError && error.status === 401) return;
      const message =
        error instanceof ApiError
          ? error.message
          : "No hay conexión con la API para comprobar la sesión.";
      setPhase({ kind: "offline", message });
      throw error;
    }
  }, []);

  const value = useMemo(() => ({ phase, retry, refresh }), [phase, retry, refresh]);

  return (
    <SessionContext.Provider value={value}>
      {phase.kind === "in" ? (
        <AppHeader email={phase.me.email} />
      ) : (
        <header className="site-header">
          <div className="wrap header-inner">
            <p className="product">
              Nexova <span>Portal interno</span>
            </p>
          </div>
        </header>
      )}
      <main id="contenido" className="session-main">
        <div className="wrap">
          {phase.kind === "checking" ? <LoadingState label="Comprobando la sesión…" /> : null}
          {phase.kind === "offline" ? (
            <ErrorBanner
              heading="h1"
              title="No se pudo comprobar la sesión"
              message={phase.message}
              onRetry={retry}
            />
          ) : null}
          {phase.kind === "in" ? children : null}
        </div>
      </main>
    </SessionContext.Provider>
  );
}
