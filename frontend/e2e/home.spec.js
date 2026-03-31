import { test, expect } from "@playwright/test";
import { mockApi } from "./helpers.js";

test.describe("Home page", () => {
  test.beforeEach(async ({ page }) => {
    await mockApi(page);
  });

  test("displays the home page with title and resource cards", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toHaveText("CRUD App");
    await expect(page.locator(".home-cards")).toBeVisible();
  });

  test("navbar links navigate correctly", async ({ page }) => {
    await page.goto("/");

    await page.click('.navbar-links a:has-text("Items")');
    await expect(page).toHaveURL(/\/items/);
    await expect(page.locator("h1")).toHaveText("Items");

    await page.click('.navbar-links a:has-text("Groups")');
    await expect(page).toHaveURL(/\/groups/);
    await expect(page.locator("h1")).toHaveText("Groups");

    await page.click(".navbar-brand a");
    await expect(page).toHaveURL("/");
  });
});
