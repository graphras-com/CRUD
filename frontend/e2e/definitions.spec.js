import { test, expect } from "@playwright/test";
import { mockApi } from "./helpers.js";

test.describe("Details CRUD", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("adds a new detail and redirects to item list scrolled to the item", async ({ page }) => {
    await page.goto("/items");

    // Click "+ Detail" on Widget (scoped to item-level actions)
    const widgetEntry = page.locator(".detail-card-entry:has-text('Widget')");
    await widgetEntry.locator('.detail-card-actions a:has-text("+ Detail")').click();
    await expect(page).toHaveURL(/\/items\/\d+\/details\/new/);

    // Should show item name in heading
    await expect(page.locator("h1")).toContainText("Widget");

    // Fill in new detail
    const descTextarea = page.locator(".form-group").filter({ hasText: "Description" }).locator("textarea");
    await descTextarea.fill("An alternative component for mobile views.");
    const notesTextarea = page.locator(".form-group").filter({ hasText: "Notes" }).locator("textarea");
    await notesTextarea.fill("Introduced in version 3.1.");
    await page.selectOption("select", { label: "Operations" });

    await page.click('button:has-text("Create Detail")');
    // Should redirect to the item list
    await expect(page).toHaveURL("/items");
    // The item entry should be visible
    await expect(page.locator("#item-1")).toBeVisible();
  });

  test("edits a detail and redirects to item list scrolled to the item", async ({ page }) => {
    // Navigate to Widget's detail page (item id 1)
    await page.goto("/items/1");

    // Click edit on the detail (only one detail card, so only one Edit link)
    await page.locator('.card a:has-text("Edit")').click();
    await expect(page).toHaveURL(/\/items\/1\/details\/\d+\/edit/);

    const descTextarea = page.locator(".form-group").filter({ hasText: "Description" }).locator("textarea");
    await descTextarea.clear();
    await descTextarea.fill("Updated widget description.");

    await page.click('button:has-text("Save Changes")');
    // Should redirect to the item list
    await expect(page).toHaveURL("/items");
    // The item entry should be visible (scrolled into view)
    await expect(page.locator("#item-1")).toBeVisible();
  });

  test("group dropdown shows breadcrumb labels in create form", async ({ page }) => {
    await page.goto("/items");

    // Click "+ Detail" on Widget
    const widgetEntry = page.locator(".detail-card-entry:has-text('Widget')");
    await widgetEntry.locator('.detail-card-actions a:has-text("+ Detail")').click();

    // Child groups should show full breadcrumb with » separator
    const select = page.locator("select");
    await expect(select.locator("option:has-text('Engineering \u00BB Backend')")).toBeAttached();
    await expect(select.locator("option:has-text('Design \u00BB UX')")).toBeAttached();
    await expect(select.locator("option:has-text('Operations \u00BB Infrastructure')")).toBeAttached();

    // Can select a breadcrumb option
    await select.selectOption({ label: "Engineering \u00BB Backend" });
    await expect(select).toHaveValue("engineering.backend");
  });

  test("group dropdown shows breadcrumb labels in edit form", async ({ page }) => {
    await page.goto("/items/1");

    await page.locator('.card a:has-text("Edit")').click();

    // Child groups should show full breadcrumb with » separator
    const select = page.locator("select");
    await expect(select.locator("option:has-text('Engineering \u00BB Backend')")).toBeAttached();
    await expect(select.locator("option:has-text('Design \u00BB UX')")).toBeAttached();
    await expect(select.locator("option:has-text('Operations \u00BB Infrastructure')")).toBeAttached();
  });

  test("deletes a detail from item detail page", async ({ page }) => {
    await page.goto("/items/2"); // Pipeline has 2 details

    await expect(page.locator(".card")).toHaveCount(2);

    page.on("dialog", (dialog) => dialog.accept());

    // Delete the first detail
    await page.locator(".card").first().locator('button:has-text("Delete")').click();

    await expect(page.locator(".card")).toHaveCount(1);
  });

  test("deletes a detail inline from items list view", async ({ page }) => {
    await page.goto("/items");

    // Pipeline entry has 2 details
    const pipelineEntry = page.locator(".detail-card-entry:has-text('Pipeline')");
    await expect(pipelineEntry.locator(".detail-card-child")).toHaveCount(2);

    page.on("dialog", (dialog) => dialog.accept());

    // Click delete on first detail's actions
    const firstDef = pipelineEntry.locator(".detail-card-child").first();
    await firstDef.hover();
    await firstDef.locator('button:has-text("Delete")').click();

    await expect(pipelineEntry.locator(".detail-card-child")).toHaveCount(1);
  });
});
