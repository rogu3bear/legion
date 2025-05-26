import { test, expect } from '@playwright/test';

test.describe('Legion WebUI Smoke Tests', () => {
  test('should login and edit prompts successfully', async ({ page }) => {
    // Step 1: Visit /prompts
    await page.goto('/prompts');

    // Should see login form
    await expect(page.locator('#auth-overlay')).toBeVisible();
    await expect(page.locator('#main-content')).not.toBeVisible();

    // Step 2: Log in with demo credentials
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'test123');
    await page.click('#login-btn');

    // Wait for login to complete
    await expect(page.locator('#auth-overlay')).not.toBeVisible();
    await expect(page.locator('#main-content')).toBeVisible();

    // Should see welcome message
    await expect(page.locator('#user-info')).toContainText('Welcome, testuser');

    // Wait for agents to load - check that architect option exists (options aren't "visible" until dropdown opens)
    await expect(page.locator('#agent-select option[value="architect"]')).toHaveCount(1);

    // Step 3: Select "architect" agent
    await page.selectOption('#agent-select', 'architect');

    // Wait for prompt to load
    await expect(page.locator('#prompt-editor')).not.toBeDisabled();
    await expect(page.locator('#prompt-status')).toContainText('Loaded prompt for architect');

    // Step 4: Append "\n<!-- smoke -->" to prompt and save
    const currentContent = await page.inputValue('#prompt-editor');
    const newContent = currentContent + '\n<!-- smoke -->';
    await page.fill('#prompt-editor', newContent);

    // Save button should be enabled
    await expect(page.locator('#btn-save-prompt')).not.toBeDisabled();
    await page.click('#btn-save-prompt');

    // Step 5: Verify toast appears
    await expect(page.locator('.alert-success')).toBeVisible();
    await expect(page.locator('.alert-success')).toContainText('Prompt saved successfully');

    // Step 6: Verify content persists on reload
    await page.reload();

    // Should still be logged in (token persists)
    await expect(page.locator('#main-content')).toBeVisible();

    // Wait for agents to load again - check that architect option exists
    await expect(page.locator('#agent-select option[value="architect"]')).toHaveCount(1);

    // Select architect again
    await page.selectOption('#agent-select', 'architect');

    // Wait for the prompt to actually load
    await expect(page.locator('#prompt-status')).toContainText('Loaded prompt for architect');

    // Wait a bit more for content to be filled
    await page.waitForFunction(() => {
      const editor = document.getElementById('prompt-editor') as HTMLTextAreaElement;
      return editor && editor.value.length > 0;
    });

    // Verify the smoke comment is still there
    const reloadedContent = await page.inputValue('#prompt-editor');
    expect(reloadedContent).toContain('<!-- smoke -->');
  });

  test('should handle logout correctly', async ({ page }) => {
    // Login first
    await page.goto('/prompts');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'test123');
    await page.click('#login-btn');

    await expect(page.locator('#main-content')).toBeVisible();

    // Click logout
    await page.click('#logout-btn');

    // Should return to login form
    await expect(page.locator('#auth-overlay')).toBeVisible();
    await expect(page.locator('#main-content')).not.toBeVisible();

    // Should see logout notification
    await expect(page.locator('.alert-info')).toContainText('Logged out successfully');
  });

  test('should handle invalid credentials', async ({ page }) => {
    await page.goto('/prompts');

    await page.fill('#username', 'invalid');
    await page.fill('#password', 'invalid');
    await page.click('#login-btn');

    // Should see error message
    await expect(page.locator('#login-error')).toBeVisible();
    await expect(page.locator('#login-error')).toContainText('Incorrect username or password');

    // Should still be on login form
    await expect(page.locator('#auth-overlay')).toBeVisible();
    await expect(page.locator('#main-content')).not.toBeVisible();
  });

  test('should handle session expiration', async ({ page }) => {
    // Login first
    await page.goto('/prompts');
    await page.fill('#username', 'testuser');
    await page.fill('#password', 'test123');
    await page.click('#login-btn');

    await expect(page.locator('#main-content')).toBeVisible();

    // Simulate token expiration by clearing localStorage
    await page.evaluate(() => {
      localStorage.removeItem('legion_token');
    });

    // Try to make an API call (select an agent)
    await page.selectOption('#agent-select', 'architect');

    // Should be redirected to login
    await expect(page.locator('#auth-overlay')).toBeVisible();
    await expect(page.locator('.alert-warning')).toContainText('Session expired');
  });
});
