import { test, expect } from "@playwright/test";
import { Buffer } from "node:buffer";
import { mockApi, GROUPS, ITEMS } from "./helpers.js";

test.describe("Restore page", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("displays the restore page with title and disabled button", async ({ page }) => {
    await page.goto("/restore");
    await expect(page.locator("h1")).toHaveText("Restore");
    await expect(page.locator("button.btn-danger")).toBeDisabled();
  });

  test("shows preview after selecting a valid backup file", async ({ page }) => {
    await page.goto("/restore");

    const backupData = {
      version: 1,
      groups: [{ id: "test", parent_id: null, label: "Test" }],
      items: [
        {
          name: "Example",
          details: [{ description: "An example entry", notes: null, group_id: "test" }],
        },
      ],
    };

    // Set file input with a valid JSON backup
    const fileInput = page.locator("#backup-file");
    const buffer = Buffer.from(JSON.stringify(backupData));
    await fileInput.setInputFiles({
      name: "backup.json",
      mimeType: "application/json",
      buffer,
    });

    // Preview should show
    await expect(page.locator(".card-body")).toContainText("Groups:");
    await expect(page.locator(".card-body")).toContainText("1");
    await expect(page.locator(".card-body")).toContainText("Items:");
    await expect(page.locator(".card-body")).toContainText("1");

    // Restore button should be enabled
    await expect(page.locator("button.btn-danger")).toBeEnabled();
  });

  test("shows error for invalid JSON file", async ({ page }) => {
    await page.goto("/restore");

    const fileInput = page.locator("#backup-file");
    const buffer = Buffer.from("not valid json {{{");
    await fileInput.setInputFiles({
      name: "bad.json",
      mimeType: "application/json",
      buffer,
    });

    await expect(page.locator(".error-message")).toContainText("Could not parse file as JSON");
  });

  test("shows error for JSON without required keys", async ({ page }) => {
    await page.goto("/restore");

    const fileInput = page.locator("#backup-file");
    const buffer = Buffer.from(JSON.stringify({ foo: "bar" }));
    await fileInput.setInputFiles({
      name: "incomplete.json",
      mimeType: "application/json",
      buffer,
    });

    await expect(page.locator(".error-message")).toContainText("missing");
  });

  test("restores data after confirmation", async ({ page }) => {
    await page.goto("/restore");

    const backupData = {
      version: 1,
      groups: [{ id: "restored", parent_id: null, label: "Restored" }],
      items: [
        {
          name: "NewItem",
          details: [{ description: "A new item", notes: null, group_id: "restored" }],
        },
      ],
    };

    const fileInput = page.locator("#backup-file");
    const buffer = Buffer.from(JSON.stringify(backupData));
    await fileInput.setInputFiles({
      name: "backup.json",
      mimeType: "application/json",
      buffer,
    });

    // Accept the confirm dialog
    page.on("dialog", (dialog) => dialog.accept());

    await page.click("button.btn-danger");

    // Success message should show
    await expect(page.locator(".card-body")).toContainText("Restore complete");
    await expect(page.locator(".card-body")).toContainText("1 groups");
    await expect(page.locator(".card-body")).toContainText("1 items");
  });

  test("cancelling confirmation does not restore", async ({ page }) => {
    await page.goto("/restore");

    const backupData = {
      version: 1,
      groups: [{ id: "x", parent_id: null, label: "X" }],
      items: [],
    };

    const fileInput = page.locator("#backup-file");
    const buffer = Buffer.from(JSON.stringify(backupData));
    await fileInput.setInputFiles({
      name: "backup.json",
      mimeType: "application/json",
      buffer,
    });

    // Dismiss the confirm dialog
    page.on("dialog", (dialog) => dialog.dismiss());

    await page.click("button.btn-danger");

    // No success message should appear
    await expect(page.locator("text=Restore complete")).not.toBeVisible();
    // Preview should still be visible
    await expect(page.locator(".card-header")).toContainText("Preview");
  });
});
