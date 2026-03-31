import { test, expect } from "@playwright/test";
import { mockApi } from "./helpers.js";

test.describe("Search and filter", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("search filters items by name", async ({ page }) => {
    await page.goto("/items");
    await expect(page.locator(".detail-card-entry")).toHaveCount(3);

    await page.fill('input[placeholder="Search items..."]', "wid");
    await expect(page.locator(".detail-card-entry")).toHaveCount(1);
    await expect(page.locator(".detail-card-title:has-text('Widget')")).toBeVisible();
  });

  test("search is case-insensitive", async ({ page }) => {
    await page.goto("/items");
    await page.fill('input[placeholder="Search items..."]', "PIPELINE");
    await expect(page.locator(".detail-card-entry")).toHaveCount(1);
    await expect(page.locator(".detail-card-title:has-text('Pipeline')")).toBeVisible();
  });

  test("group filter limits items to those with matching details", async ({ page }) => {
    await page.goto("/items");
    await expect(page.locator(".detail-card-entry")).toHaveCount(3);

    // The group filter select shows breadcrumb labels
    await page.locator(".filters select").selectOption({ label: "Engineering \u00BB Backend" });

    // Pipeline and Sprint have engineering.backend details
    await expect(page.locator(".detail-card-entry")).toHaveCount(2);
  });

  test("search and group filter work together", async ({ page }) => {
    await page.goto("/items");

    await page.fill('input[placeholder="Search items..."]', "pi");
    await page.locator(".filters select").selectOption({ label: "Engineering \u00BB Backend" });

    // Pipeline has an engineering.backend detail AND matches "pi"
    await expect(page.locator(".detail-card-entry")).toHaveCount(1);
    await expect(page.locator(".detail-card-title:has-text('Pipeline')")).toBeVisible();
  });

  test("clearing search shows all items again", async ({ page }) => {
    await page.goto("/items");
    await page.fill('input[placeholder="Search items..."]', "wid");
    await expect(page.locator(".detail-card-entry")).toHaveCount(1);

    await page.fill('input[placeholder="Search items..."]', "");
    await expect(page.locator(".detail-card-entry")).toHaveCount(3);
  });

  test("no results shows empty state", async ({ page }) => {
    await page.goto("/items");
    await page.fill('input[placeholder="Search items..."]', "xyznonexistent");
    await expect(page.locator(".detail-card-entry")).toHaveCount(0);
    await expect(page.locator("text=No items found.")).toBeVisible();
  });

  test("group filter dropdown shows breadcrumb labels", async ({ page }) => {
    await page.goto("/items");

    const select = page.locator(".filters select");
    // Child groups should show full breadcrumb with » separator
    await expect(select.locator("option:has-text('Engineering \u00BB Backend')")).toBeAttached();
    await expect(select.locator("option:has-text('Design \u00BB UX')")).toBeAttached();
    await expect(select.locator("option:has-text('Operations \u00BB Infrastructure')")).toBeAttached();

    // Top-level groups should show just their label
    await expect(select.locator("option[value='engineering']")).toHaveText("Engineering");
    await expect(select.locator("option[value='design']")).toHaveText("Design");
  });

  test("search text persists in URL as query param", async ({ page }) => {
    await page.goto("/items");
    await page.fill('input[placeholder="Search items..."]', "sprint");
    await expect(page).toHaveURL(/q=sprint/);
  });
});
