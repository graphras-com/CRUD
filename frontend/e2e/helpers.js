/**
 * Shared mock data and route-mocking helpers for Playwright tests.
 *
 * Every test calls `mockApi(page)` before navigating.  This intercepts
 * all requests to the FastAPI backend (http://localhost:8000/*) and
 * returns deterministic JSON so the tests run without a real server.
 *
 * The helpers return mutable references to the data arrays so individual
 * tests can inspect / mutate state when verifying CRUD behaviour.
 */

export const GROUPS = [
  { id: "engineering", parent_id: null, label: "Engineering" },
  { id: "engineering.backend", parent_id: "engineering", label: "Backend" },
  { id: "design", parent_id: null, label: "Design" },
  { id: "design.ux", parent_id: "design", label: "UX" },
  { id: "operations", parent_id: null, label: "Operations" },
  {
    id: "operations.infrastructure",
    parent_id: "operations",
    label: "Infrastructure",
  },
];

export const ITEMS = [
  {
    id: 1,
    name: "Widget",
    details: [
      {
        id: 10,
        description: "A reusable UI component for dashboards.",
        notes: "Used in version 2.0 and later.",
        group_id: "design",
      },
    ],
  },
  {
    id: 2,
    name: "Pipeline",
    details: [
      {
        id: 20,
        description: "An automated sequence of build and deploy steps.",
        notes: null,
        group_id: "engineering.backend",
      },
      {
        id: 21,
        description: "A data processing pipeline for ETL workflows.",
        notes: "Runs nightly via cron job.",
        group_id: "operations",
      },
    ],
  },
  {
    id: 3,
    name: "Sprint",
    details: [
      {
        id: 30,
        description: "A fixed time period for completing a set of tasks.",
        notes: null,
        group_id: "engineering.backend",
      },
    ],
  },
];

let nextItemId = 100;
let nextDetailId = 1000;

/**
 * Intercept all backend API calls and respond with mock data.
 * Returns `{ groups, items }` so tests can inspect state.
 */
export async function mockApi(page) {
  const groups = structuredClone(GROUPS);
  const items = structuredClone(ITEMS);
  nextItemId = 100;
  nextDetailId = 1000;

  // ── Catch-all for API requests ──
  // Matches requests to the Vite dev server (localhost:5173) for API paths,
  // or direct requests to the backend (localhost:8000).
  // We check the Accept header to avoid intercepting HTML page navigations.
  await page.route(/localhost:(5173|8000)\/(groups|items|backup|health)/, async (route) => {
    // Let page navigations (HTML requests) pass through to Vite dev server
    const accept = route.request().headers()["accept"] || "";
    if (accept.includes("text/html")) {
      return route.fallback();
    }

    const method = route.request().method();
    const url = route.request().url();
    const parsed = new URL(url);
    const pathname = parsed.pathname.replace(/\/$/, ""); // normalize: strip trailing slash

    // ── Groups list: /groups ──
    if (pathname === "/groups") {
      if (method === "GET") {
        return route.fulfill({ json: groups });
      }
      if (method === "POST") {
        const body = route.request().postDataJSON();
        const grp = {
          id: body.id,
          parent_id: body.parent_id || null,
          label: body.label,
        };
        groups.push(grp);
        return route.fulfill({ status: 201, json: grp });
      }
      return route.fallback();
    }

    // ── Group detail: /groups/{id} ──
    const groupDetailMatch = pathname.match(/^\/groups\/(.+)$/);
    if (groupDetailMatch) {
      const id = decodeURIComponent(groupDetailMatch[1]);
      const idx = groups.findIndex((g) => g.id === id);

      if (method === "GET") {
        if (idx === -1)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        return route.fulfill({ json: groups[idx] });
      }
      if (method === "PATCH") {
        if (idx === -1)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const body = route.request().postDataJSON();
        if (body.label !== undefined) groups[idx].label = body.label;
        if (body.parent_id !== undefined)
          groups[idx].parent_id = body.parent_id;
        return route.fulfill({ json: groups[idx] });
      }
      if (method === "DELETE") {
        if (idx === -1)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        groups.splice(idx, 1);
        return route.fulfill({ status: 204, body: "" });
      }
      return route.fallback();
    }

    // ── Items list: /items ──
    if (pathname === "/items") {
      if (method === "GET") {
        const q = parsed.searchParams.get("q")?.toLowerCase();
        const grp = parsed.searchParams.get("group");
        let result = items;
        if (q)
          result = result.filter((i) => i.name.toLowerCase().includes(q));
        if (grp)
          result = result.filter((i) =>
            i.details.some((d) => d.group_id === grp)
          );
        return route.fulfill({ json: result });
      }
      if (method === "POST") {
        const body = route.request().postDataJSON();
        const item = {
          id: ++nextItemId,
          name: body.name,
          details: body.details.map((d) => ({
            id: ++nextDetailId,
            description: d.description,
            notes: d.notes || null,
            group_id: d.group_id,
          })),
        };
        items.push(item);
        return route.fulfill({ status: 201, json: item });
      }
      return route.fallback();
    }

    // ── Item details: /items/{id}/details or /items/{id}/details/{detailId} ──
    const detailDetailMatch = pathname.match(
      /^\/items\/(\d+)\/details\/(\d+)$/
    );
    if (detailDetailMatch) {
      const itemId = Number(detailDetailMatch[1]);
      const detailId = Number(detailDetailMatch[2]);
      const item = items.find((i) => i.id === itemId);

      if (method === "PATCH") {
        if (!item)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const det = item.details.find((d) => d.id === detailId);
        if (!det)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const body = route.request().postDataJSON();
        if (body.description !== undefined) det.description = body.description;
        if (body.notes !== undefined) det.notes = body.notes;
        if (body.group_id !== undefined) det.group_id = body.group_id;
        return route.fulfill({ json: det });
      }
      if (method === "DELETE") {
        if (!item)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const idx = item.details.findIndex((d) => d.id === detailId);
        if (idx === -1)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        item.details.splice(idx, 1);
        return route.fulfill({ status: 204, body: "" });
      }
      return route.fallback();
    }

    const detailListMatch = pathname.match(/^\/items\/(\d+)\/details$/);
    if (detailListMatch) {
      const itemId = Number(detailListMatch[1]);
      const item = items.find((i) => i.id === itemId);

      if (method === "POST") {
        if (!item)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const body = route.request().postDataJSON();
        const det = {
          id: ++nextDetailId,
          description: body.description,
          notes: body.notes || null,
          group_id: body.group_id,
        };
        item.details.push(det);
        return route.fulfill({ status: 201, json: det });
      }
      return route.fallback();
    }

    // ── Item detail: /items/{id} ──
    const itemDetailMatch = pathname.match(/^\/items\/(\d+)$/);
    if (itemDetailMatch) {
      const itemId = Number(itemDetailMatch[1]);
      const item = items.find((i) => i.id === itemId);

      if (method === "GET") {
        if (!item)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        return route.fulfill({ json: item });
      }
      if (method === "PATCH") {
        if (!item)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        const body = route.request().postDataJSON();
        if (body.name !== undefined) item.name = body.name;
        return route.fulfill({ json: item });
      }
      if (method === "DELETE") {
        const idx = items.findIndex((i) => i.id === itemId);
        if (idx === -1)
          return route.fulfill({
            status: 404,
            json: { detail: "Not found" },
          });
        items.splice(idx, 1);
        return route.fulfill({ status: 204, body: "" });
      }
      return route.fallback();
    }

    // ── Backup: /backup ──
    if (pathname === "/backup") {
      if (method === "GET") {
        return route.fulfill({
          json: {
            version: 1,
            groups: groups.map((g) => ({
              id: g.id,
              parent_id: g.parent_id,
              label: g.label,
            })),
            items: items.map((i) => ({
              name: i.name,
              details: i.details.map((d) => ({
                description: d.description,
                notes: d.notes,
                group_id: d.group_id,
              })),
            })),
          },
        });
      }
      return route.fallback();
    }

    // ── Restore: /backup/restore ──
    if (pathname === "/backup/restore") {
      if (method === "POST") {
        const body = route.request().postDataJSON();
        // Replace mock data
        groups.length = 0;
        if (body.groups) body.groups.forEach((g) => groups.push(g));
        items.length = 0;
        if (body.items) {
          body.items.forEach((i, idx) => {
            items.push({
              id: idx + 1,
              name: i.name,
              details: (i.details || []).map((d, j) => ({
                id: (idx + 1) * 100 + j,
                description: d.description,
                notes: d.notes || null,
                group_id: d.group_id,
              })),
            });
          });
        }
        return route.fulfill({
          json: {
            status: "ok",
            groups: groups.length,
            items: items.length,
          },
        });
      }
      return route.fallback();
    }

    // Unmatched – let it fall through
    return route.fallback();
  });

  return { groups, items };
}
