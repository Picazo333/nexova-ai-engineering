"use client";

import { useMemo } from "react";
import { createApi, type TrackerApi } from "@/lib/api";
import { getApiBaseUrl } from "@/lib/env";

export function useTracker(): TrackerApi {
  return useMemo(() => createApi(getApiBaseUrl()), []);
}
