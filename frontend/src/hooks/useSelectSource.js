import { useEffect, useState, useCallback, useMemo } from "react";
import { api } from "../api/client";
import { resources } from "../config/resources";
import { buildBreadcrumb } from "../utils/breadcrumb";

/**
 * Collect every distinct `source` value used by select fields across all
 * resources (including children).
 */
function collectSources() {
  const sources = new Set();
  for (const resource of resources) {
    for (const field of resource.fields || []) {
      if (field.type === "select" && field.source) sources.add(field.source);
    }
    for (const child of resource.children || []) {
      for (const field of child.fields || []) {
        if (field.type === "select" && field.source) sources.add(field.source);
      }
    }
    for (const filter of resource.filters || []) {
      if (filter.source) sources.add(filter.source);
    }
  }
  return sources;
}

/**
 * Custom hook that fetches data for every select-source resource and
 * exposes helpers for looking up items and building breadcrumbs.
 *
 * Returns:
 *   - sourceData   — { [sourceName]: item[] }
 *   - sourceMap    — { [sourceName]: { [id]: item } }
 *   - getItems(sourceName) — returns the raw array for a source
 *   - breadcrumb(sourceName, id) — returns a breadcrumb string
 */
export default function useSelectSource() {
  const sourceNames = useMemo(() => collectSources(), []);
  const [sourceData, setSourceData] = useState({});
  const [sourceMap, setSourceMap] = useState({});

  useEffect(() => {
    for (const name of sourceNames) {
      if (!api[name]) continue;
      api[name]
        .list()
        .then((items) => {
          setSourceData((prev) => ({ ...prev, [name]: items }));
          const map = {};
          items.forEach((item) => (map[item.id] = item));
          setSourceMap((prev) => ({ ...prev, [name]: map }));
        })
        .catch(() => {});
    }
  }, [sourceNames]);

  const getItems = useCallback(
    (sourceName) => sourceData[sourceName] || [],
    [sourceData],
  );

  const breadcrumb = useCallback(
    (sourceName, id) => buildBreadcrumb(id, sourceMap[sourceName] || {}),
    [sourceMap],
  );

  return { sourceData, sourceMap, getItems, breadcrumb };
}
