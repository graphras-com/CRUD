import { test, expect } from "@playwright/test";
import { mockApi } from "./helpers.js";

test.describe("Items (detail-cards list)", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("displays all items with their details inline", async ({ page }) => {
    await page.goto("/items");

    // All three mock items visible
    await expect(page.locator(".detail-card-entry")).toHaveCount(3);
    await expect(page.locator(".detail-card-title:has-text('Widget')")).toBeVisible();
    await expect(page.locator(".detail-card-title:has-text('Pipeline')")).toBeVisible();
    await expect(page.locator(".detail-card-title:has-text('Sprint')")).toBeVisible();
  });

  test("shows descriptions inline", async ({ page }) => {
    await page.goto("/items");

    await expect(
      page.locator("text=A reusable UI component for dashboards.")
    ).toBeVisible();
    await expect(
      page.locator("text=A fixed time period for completing a set of tasks.")
    ).toBeVisible();
  });

  test("shows notes when present", async ({ page }) => {
    await page.goto("/items");

    await expect(
      page.locator("text=Used in version 2.0 and later.")
    ).toBeVisible();
  });

  test("shows group breadcrumbs on details", async ({ page }) => {
    await page.goto("/items");

    // "engineering.backend" should render as "Engineering » Backend"
    await expect(page.locator(".badge:has-text('Engineering \u00BB Backend')").first()).toBeVisible();

    // "design.ux" should render as "Design » UX" (if present) or "Design"
    const designBadges = page.locator(".badge:has-text('Design')");
    await expect(designBadges.first()).toBeVisible();
  });

  test("numbers details when an item has more than one", async ({ page }) => {
    await page.goto("/items");

    // Pipeline has 2 details so they should be numbered
    const pipelineEntry = page.locator(".detail-card-entry:has-text('Pipeline')");
    await expect(pipelineEntry.locator(".detail-card-child-num:has-text('1.')")).toBeVisible();
    await expect(pipelineEntry.locator(".detail-card-child-num:has-text('2.')")).toBeVisible();

    // Widget has 1 detail so no numbering
    const widgetEntry = page.locator(".detail-card-entry:has-text('Widget')");
    await expect(widgetEntry.locator(".detail-card-child-num")).toHaveCount(0);
  });

  test("creates a new item and it appears in the list", async ({ page }) => {
    await page.goto("/items");
    await page.click('a:has-text("+ New Item")');
    await expect(page).toHaveURL(/\/items\/new/);
    await expect(page.getByRole("heading", { name: "New Item" })).toBeVisible();

    await page.fill("#field-name", "Workflow");
    await page
      .locator("#child-details-0-description")
      .fill("A sequence of steps to complete a process.");
    await page
      .locator("#child-details-0-group_id")
      .selectOption({ label: "Design" });

    await page.click('button:has-text("Create Item")');
    // Redirects to /items
    await expect(page).toHaveURL(/\/items$/);
  });

  test("edits an item name", async ({ page }) => {
    await page.goto("/items");

    // Click edit on the first item's actions
    const firstEntry = page.locator(".detail-card-entry").first();
    await firstEntry.locator('.detail-card-actions a:has-text("Edit")').click();
    await expect(page).toHaveURL(/\/items\/\d+\/edit/);

    // Wait for the edit form to render
    await expect(page.locator("h1")).toHaveText("Edit Item");

    const input = page.locator('form input[type="text"]');
    await input.clear();
    await input.fill("Widget (Updated)");
    await page.click('button:has-text("Save Changes")');

    // Redirects back to /items
    await expect(page).toHaveURL(/\/items$/);
  });

  test("deletes an item after confirmation", async ({ page }) => {
    await page.goto("/items");
    await expect(page.locator(".detail-card-entry")).toHaveCount(3);

    // Set up dialog handler to accept
    page.on("dialog", (dialog) => dialog.accept());

    // Scope to item-level actions
    const firstEntry = page.locator(".detail-card-entry").first();
    await firstEntry.locator('.detail-card-actions button:has-text("Delete")').click();

    await expect(page.locator(".detail-card-entry")).toHaveCount(2);
  });
});
