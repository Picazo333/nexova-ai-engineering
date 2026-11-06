"use client";

import { useEffect } from "react";

export function MotionPref() {
  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => {
      document.documentElement.dataset.motion = query.matches ? "reduced" : "full";
    };
    apply();
    query.addEventListener("change", apply);
    return () => query.removeEventListener("change", apply);
  }, []);
  return null;
}
