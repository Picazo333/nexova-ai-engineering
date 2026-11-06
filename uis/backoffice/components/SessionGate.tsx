"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { InventoryNav } from "@/components/inventory/InventoryNav";
import { fetchMe, type AuthMe } from "@/lib/auth";
import { ApiError } from "@/lib/http";
import { loginRedirect } from "@/lib/paths";
import { clearToken, readToken } from "@/lib/session";

type Phase =
  | { kind: "checking" }
  | { kind: "redirecting" }
  | { kind: "in"; me: AuthMe }
  | { kind: "offline"; message: string };

export function SessionGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname() || "/backoffice/inventory/products";
  const [phase, setPhase] = useState<Phase>({ kind: "checking" });
  const [attempt, setAttempt] = useState(0);
  const retry = useCallback(() => setAttempt((value) => value + 1), []);

  useEffect(() => {
    let cancelled = false;
    const search = window.location.search;
    const target = loginRedirect(pathname, search, readToken());
    if (target) {
      setPhase({ kind: "redirecting" });
      router.replace(target);
      return () => {
        cancelled = true;
      };
    }
    setPhase({ kind: "checking" });
    fetchMe()
      .then((me) => {
        if (!cancelled) setPhase({ kind: "in", me });
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 401) return;
        const message = error instanceof ApiError ? error.message : "No hay conexión con la API para comprobar la sesión.";
        setPhase({ kind: "offline", message });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, pathname, router]);

  function logout() {
    clearToken();
    router.replace("/login");
  }

  if (phase.kind === "in") {
    return (
      <main id="contenido" className="panel">
        <div className="wrap">
          <div className="session-bar">
            <p className="note">
              Sesión de {phase.me.email}. user_uuid <span className="mono">{phase.me.id}</span>.
            </p>
            <button type="button" className="secondary" onClick={logout}>
              Cerrar sesión
            </button>
          </div>
          <InventoryNav />
          {children}
        </div>
      </main>
    );
  }

  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        {phase.kind === "checking" ? <LoadingState label="Comprobando la sesión…" /> : null}
        {phase.kind === "redirecting" ? <LoadingState label="Redirigiendo al inicio de sesión…" /> : null}
        {phase.kind === "offline" ? (
          <ErrorBanner heading="h1" title="No se pudo comprobar la sesión" message={phase.message} onRetry={retry} />
        ) : null}
      </div>
    </main>
  );
}
