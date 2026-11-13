/**
 * Maps a Web Vital into the 1.1.0 allowlist and sends it through track().
 * FID and routes outside the closed list are dropped. No DOM node, no metric id.
 */

import { canonicalPath, track } from "@/lib/telemetry";

export const WEB_VITALS = ["LCP", "INP", "CLS", "FCP", "TTFB"] as const;
export type WebVitalName = (typeof WEB_VITALS)[number];
export type WebVitalRating = "good" | "needs-improvement" | "poor";

const CUTS: Record<WebVitalName, readonly [number, number]> = {
  LCP: [2500, 4000],
  INP: [200, 500],
  CLS: [0.1, 0.25],
  FCP: [1800, 3000],
  TTFB: [800, 1800],
};

export function isWebVitalName(name: string): name is WebVitalName {
  return (WEB_VITALS as readonly string[]).includes(name);
}

export function rateWebVital(name: WebVitalName, value: number): WebVitalRating {
  const [good, needsImprovement] = CUTS[name];
  if (value <= good) return "good";
  if (value <= needsImprovement) return "needs-improvement";
  return "poor";
}

export function webVitalProperties(input: {
  name: string;
  value: number;
  pathname: string;
}): Record<string, unknown> | null {
  if (!isWebVitalName(input.name)) return null;
  if (!Number.isFinite(input.value) || input.value < 0 || input.value > 600_000) return null;
  const path = canonicalPath(input.pathname);
  if (!path) return null;
  return {
    app: "backoffice",
    path_template: path,
    metric_name: input.name,
    value: input.value,
    rating: rateWebVital(input.name, input.value),
  };
}

export function trackWebVital(input: { name: string; value: number; pathname: string }): void {
  const properties = webVitalProperties(input);
  if (!properties) return;
  track("web_vital_recorded", properties);
}
