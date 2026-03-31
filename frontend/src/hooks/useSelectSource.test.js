import { describe, it, expect } from "vitest";
import { buildBreadcrumb } from "../utils/breadcrumb";

describe("buildBreadcrumb", () => {
  const itemMap = {
    root: { id: "root", label: "Root", parent_id: null },
    child: { id: "child", label: "Child", parent_id: "root" },
    grandchild: { id: "grandchild", label: "Grandchild", parent_id: "child" },
  };

  it("returns the label for a top-level item", () => {
    expect(buildBreadcrumb("root", itemMap)).toBe("Root");
  });

  it("builds a breadcrumb for a child item", () => {
    expect(buildBreadcrumb("child", itemMap)).toBe("Root \u00BB Child");
  });

  it("builds a full breadcrumb for a deeply nested item", () => {
    expect(buildBreadcrumb("grandchild", itemMap)).toBe(
      "Root \u00BB Child \u00BB Grandchild",
    );
  });

  it("returns the raw id when item is not in the map", () => {
    expect(buildBreadcrumb("unknown", itemMap)).toBe("unknown");
  });

  it("falls back to name when label is missing", () => {
    const map = { a: { id: "a", name: "Alpha", parent_id: null } };
    expect(buildBreadcrumb("a", map)).toBe("Alpha");
  });

  it("falls back to id when both label and name are missing", () => {
    const map = { x: { id: "x", parent_id: null } };
    expect(buildBreadcrumb("x", map)).toBe("x");
  });
});
