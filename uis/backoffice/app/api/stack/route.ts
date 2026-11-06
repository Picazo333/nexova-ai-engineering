import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function upstream(raw: string): { origin: string; label: string } | { error: string } {
  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    return { error: "API_INTERNAL_URL no es una URL." };
  }
  const host = parsed.hostname;
  if (host === "localhost" || host === "127.0.0.1" || /^\d+\.\d+\.\d+\.\d+$/.test(host)) {
    return { error: "La API interna no puede usar localhost ni una IP fija." };
  }
  const port = parsed.port || (parsed.protocol === "https:" ? "443" : "80");
  return { origin: raw.replace(/\/$/, ""), label: `${host}:${port}` };
}

export async function GET() {
  const raw = process.env.API_INTERNAL_URL?.trim() ?? "";
  if (!raw) {
    return NextResponse.json({ ok: false, message: "Falta API_INTERNAL_URL." });
  }
  const target = upstream(raw);
  if ("error" in target) {
    return NextResponse.json({ ok: false, message: target.error });
  }
  try {
    const response = await fetch(`${target.origin}/health`, { cache: "no-store" });
    if (!response.ok) {
      return NextResponse.json(
        { ok: false, upstream: target.label, message: `La API respondió ${response.status}.` },
        { status: 502 },
      );
    }
    const body = (await response.json()) as { status?: string };
    return NextResponse.json({
      ok: true,
      upstream: target.label,
      status: body.status === "ok" ? "ok" : "desconocido",
    });
  } catch {
    return NextResponse.json(
      { ok: false, upstream: target.label, message: "No hay conexión con la API." },
      { status: 502 },
    );
  }
}
