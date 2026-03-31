import { test, expect } from "@playwright/test";
import { mockApi } from "./helpers.js";

test.describe("Groups CRUD", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("displays all groups in a table", async ({ page }) => {
    await page.goto("/groups");

    await expect(page.locator("h1")).toHaveText("Groups");
    await expect(page.locator("table tbody tr")).toHaveCount(6);
    // Use exact text match for label cells to avoid matching ID/parent columns
    await expect(page.getByRole("cell", { name: "Engineering", exact: true })).toBeVisible();
    await expect(page.getByRole("cell", { name: "Design", exact: true })).toBeVisible();
    await expect(page.getByRole("cell", { name: "Operations", exact: true })).toBeVisible();
  });

  test("shows parent group IDs where present", async ({ page }) => {
    await page.goto("/groups");

    // Backend row should show parent "engineering" — use exact text match for code
    const backendRow = page.locator("tr:has(code:text-is('engineering.backend'))");
    // The parent column should have code element with exact text "engineering"
    await expect(backendRow.locator("code:text-is('engineering')")).toBeVisible();

    // Engineering (top-level) should show "--"
    const allEngineeringRows = page.locator("tr:has(code:text-is('engineering'))");
    const engineeringRow = allEngineeringRows.first();
    await expect(engineeringRow.locator(".muted")).toBeVisible();
  });

  test("creates a new group", async ({ page }) => {
    await page.goto("/groups");
    await page.click('a:has-text("+ New Group")');
    await expect(page).toHaveURL(/\/groups\/new/);

    await page.fill('input[placeholder*="e.g."]', "design.visual");
    // Label field – second input
    const labelInput = page.locator(".form-group").filter({ hasText: "Label" }).locator("input");
    await labelInput.fill("Visual");
    // Select option uses "{label} ({id})" format
    await page.selectOption("select", { label: "Design (design)" });

    await page.click('button:has-text("Create Group")');
    await expect(page).toHaveURL(/\/groups$/);
    // New group should now appear
    await expect(page.locator("table tbody tr")).toHaveCount(7);
  });

  test("edits a group", async ({ page }) => {
    await page.goto("/groups");

    const firstRow = page.locator("table tbody tr").first();
    await firstRow.locator('a:has-text("Edit")').click();
    await expect(page).toHaveURL(/\/groups\/.+\/edit/);

    const labelInput = page.locator(".form-group").filter({ hasText: "Label" }).locator("input");
    await labelInput.clear();
    await labelInput.fill("Engineering (Updated)");
    await page.click('button:has-text("Save Changes")');
    await expect(page).toHaveURL(/\/groups$/);
  });

  test("deletes a group after confirmation", async ({ page }) => {
    await page.goto("/groups");
    await expect(page.locator("table tbody tr")).toHaveCount(6);

    page.on("dialog", (dialog) => dialog.accept());

    const lastRow = page.locator("table tbody tr").last();
    await lastRow.locator('button:has-text("Delete")').click();

    await expect(page.locator("table tbody tr")).toHaveCount(5);
  });

  test("cancel button returns to list without saving", async ({ page }) => {
    await page.goto("/groups/new");
    await page.click('button:has-text("Cancel")');
    await expect(page).toHaveURL(/\/groups$/);
  });
});
