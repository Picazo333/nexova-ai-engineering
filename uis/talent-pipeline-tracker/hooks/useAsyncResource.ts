"use client";

import { useEffect, useState } from "react";
import { isAbortError, toErrorMessage } from "@/lib/errors";

export type AsyncStatus = "loading" | "success" | "error";

export interface AsyncResource<T> {
  status: AsyncStatus;
  data?: T;
  error?: string;
  retry: () => void;
}

interface ResourceState<T> {
  status: AsyncStatus;
  data?: T;
  error?: string;
  key: string;
  attempt: number;
}

export function useAsyncResource<T>(
  key: string,
  loader: (signal: AbortSignal) => Promise<T>,
): AsyncResource<T> {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<ResourceState<T>>({
    status: "loading",
    key,
    attempt: 0,
  });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    loader(controller.signal)
      .then((data) => {
        if (!active) return;
        setState({ status: "success", data, key, attempt });
      })
      .catch((error: unknown) => {
        if (!active || isAbortError(error)) return;
        setState((previous) => ({
          status: "error",
          error: toErrorMessage(error),
          data: previous.key === key ? previous.data : undefined,
          key,
          attempt,
        }));
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [attempt, key, loader]);

  const current = state.key === key && state.attempt === attempt;
  return {
    status: current ? state.status : "loading",
    data: state.key === key ? state.data : undefined,
    error: current ? state.error : undefined,
    retry: () => setAttempt((value) => value + 1),
  };
}
