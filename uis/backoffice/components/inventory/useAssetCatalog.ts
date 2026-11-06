"use client";

import { useEffect, useState } from "react";

import { beginCatalog, failCatalog, settleCatalog, type CatalogView } from "@/lib/catalog";
import { messageOf } from "@/lib/http";
import { listAssets, type Asset } from "@/lib/inventory";

export function useAssetCatalog(attempt: number): CatalogView<Asset> {
  const [view, setView] = useState<CatalogView<Asset>>({ phase: "loading", rows: [], error: "" });

  useEffect(() => {
    let current = true;
    setView((previous) => beginCatalog(previous.rows));
    listAssets()
      .then((rows) => {
        if (current) setView(settleCatalog(rows));
      })
      .catch((reason: unknown) => {
        if (!current) return;
        setView((previous) => failCatalog(previous.rows, messageOf(reason)));
      });
    return () => {
      current = false;
    };
  }, [attempt]);

  return view;
}
