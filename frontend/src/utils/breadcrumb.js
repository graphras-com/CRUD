/**
 * Build a breadcrumb string for a hierarchical item by walking up the
 * parent chain.  Works with any resource that has a `parent_id` field.
 *
 * @param {string} id
 * @param {Record<string, object>} itemMap — keyed by id
 * @returns {string} e.g. "Top Level >> Child"
 */
export function buildBreadcrumb(id, itemMap) {
  const parts = [];
  let current = itemMap[id];
  while (current) {
    parts.unshift(current.label || current.name || current.id);
    current = current.parent_id ? itemMap[current.parent_id] : null;
  }
  return parts.length > 0 ? parts.join(" \u00BB ") : String(id);
}
