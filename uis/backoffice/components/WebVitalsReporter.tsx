"use client";

import { useReportWebVitals } from "next/web-vitals";

import { trackWebVital } from "@/lib/web-vitals";

export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    const pathname = typeof window === "undefined" ? "/" : window.location.pathname;
    trackWebVital({ name: metric.name, value: metric.value, pathname });
  });
  return null;
}
