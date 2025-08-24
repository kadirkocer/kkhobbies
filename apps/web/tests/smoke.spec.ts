import { test, expect } from '@playwright/test';

test.describe('Hobby Showcase Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for testing
    await page.route('/api/**', (route) => {
      // Mock login response
      if (route.request().url().includes('/api/auth/login') && route.request().method() === 'POST') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            user: { id: 1, username: 'admin', name: 'Admin User' }
          })
        });
        return;
      }
      
      // Mock hobbies response
      if (route.request().url().includes('/api/hobbies')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { id: 1, name: 'Photography', color: '#00bbf9', icon: 'camera', parent_id: null },
            { id: 2, name: 'Music', color: '#9b5de5', icon: 'music', parent_id: null }
          ])
        });
        return;
      }
      
      // Mock hobby types response
      if (route.request().url().includes('/api/hobby-types')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 1,
              key: 'photo',
              title: 'Photo',
              schema_json: '{"type":"object","properties":{"camera":{"type":"string"},"lens":{"type":"string"}}}'
            }
          ])
        });
        return;
      }
      
      // Mock entries response
      if (route.request().url().includes('/api/entries')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: 1,
                hobby_id: 1,
                type_key: 'photo',
                title: 'Test Entry',
                description: 'Test description',
                tags: 'test,example',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
                media_count: 1,
                thumbnail_url: null,
                props: {}
              }
            ],
            total: 1,
            limit: 20,
            offset: 0,
            has_more: false
          })
        });
        return;
      }
      
      // Mock single entry response
      if (route.request().url().match(/\/api\/entries\/\d+$/)) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            hobby_id: 1,
            type_key: 'photo',
            title: 'Test Entry',
            description: 'Test description',
            tags: 'test,example',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          })
        });
        return;
      }
      
      // Mock entry props response
      if (route.request().url().includes('/props')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            { id: 1, entry_id: 1, key: 'camera', value_text: 'Canon EOS R5' }
          ])
        });
        return;
      }
      
      // Mock entry media response
      if (route.request().url().includes('/media')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
        return;
      }
      
      // Mock search response
      if (route.request().url().includes('/api/search')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              {
                id: 1,
                hobby_id: 1,
                type_key: 'photo',
                title: 'Searched Entry',
                description: 'Found via search',
                tags: 'photography',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z',
                media_count: 0,
                thumbnail_url: null,
                props: {}
              }
            ],
            total: 1,
            limit: 20,
            offset: 0,
            has_more: false
          })
        });
        return;
      }
      
      // Default: continue with original request
      route.continue();
    });
  });

  test('login flow works', async ({ page }) => {
    await page.goto('/login');
    
    // Should see login form
    await expect(page.locator('h2')).toContainText('Hobby Showcase');
    
    // Fill in password and submit
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // Should redirect to entries page
    await expect(page).toHaveURL('/entries');
  });

  test('entries page loads with sidebar', async ({ page }) => {
    // Go directly to entries page (mocked auth)
    await page.goto('/entries');
    
    // Should see sidebar with hobbies
    await expect(page.locator('text=Hobbies')).toBeVisible();
    await expect(page.locator('text=Photography')).toBeVisible();
    await expect(page.locator('text=Music')).toBeVisible();
    
    // Should see entries header
    await expect(page.locator('h1')).toContainText('Entries');
    
    // Should see New Entry button
    await expect(page.locator('text=New Entry')).toBeVisible();
    
    // Should see search input
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
  });

  test('can create new hobby from sidebar', async ({ page }) => {
    await page.goto('/entries');
    
    // Click Add Hobby button
    await page.click('text=Add Hobby');
    
    // Should see form
    await expect(page.locator('input[placeholder="Hobby name"]')).toBeVisible();
    
    // Fill in hobby name
    await page.fill('input[placeholder="Hobby name"]', 'Test Hobby');
    
    // Click Add button
    await page.click('button:text("Add")');
    
    // Form should disappear
    await expect(page.locator('input[placeholder="Hobby name"]')).not.toBeVisible();
  });

  test('search functionality works', async ({ page }) => {
    await page.goto('/entries');
    
    // Fill in search query
    await page.fill('input[placeholder*="Search"]', 'photography');
    
    // Submit search
    await page.press('input[placeholder*="Search"]', 'Enter');
    
    // Should see search results
    await expect(page.locator('text=Searched Entry')).toBeVisible();
  });

  test('can navigate to entry details', async ({ page }) => {
    await page.goto('/entries');
    
    // Click on an entry
    await page.click('text=Test Entry');
    
    // Should navigate to entry detail page
    await expect(page).toHaveURL('/entries/1');
    
    // Should see entry details
    await expect(page.locator('h1')).toContainText('Test Entry');
    await expect(page.locator('text=Details')).toBeVisible();
    await expect(page.locator('text=Properties')).toBeVisible();
    await expect(page.locator('text=Media')).toBeVisible();
  });

  test('entry detail page shows properties form', async ({ page }) => {
    await page.goto('/entries/1');
    
    // Should see properties section
    await expect(page.locator('text=Properties')).toBeVisible();
    
    // Click Edit button
    await page.click('button:text("Edit")');
    
    // Should see form fields based on schema
    await expect(page.locator('label:text("camera")')).toBeVisible();
    await expect(page.locator('label:text("lens")')).toBeVisible();
    
    // Should see Save and Cancel buttons
    await expect(page.locator('button:text("Save")')).toBeVisible();
    await expect(page.locator('button:text("Cancel")')).toBeVisible();
  });

  test('media upload panel is present', async ({ page }) => {
    await page.goto('/entries/1');
    
    // Should see media section
    await expect(page.locator('text=Media')).toBeVisible();
    
    // Should see upload button
    await expect(page.locator('label:text("Upload")')).toBeVisible();
    
    // Should see no media message
    await expect(page.locator('text=No media files')).toBeVisible();
  });

  test('can navigate back from entry detail', async ({ page }) => {
    await page.goto('/entries/1');
    
    // Click back button
    await page.click('text=Back to Entries');
    
    // Should return to entries page
    await expect(page).toHaveURL('/entries');
  });
});