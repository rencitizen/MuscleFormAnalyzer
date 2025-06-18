import { test, expect } from '@playwright/test';

test.describe('認証フロー', () => {
  test.beforeEach(async ({ page }) => {
    // ホームページに移動
    await page.goto('/');
  });

  test('未認証ユーザーはログインページにリダイレクトされる', async ({ page }) => {
    // ダッシュボードにアクセスを試みる
    await page.goto('/dashboard');
    
    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('ログインフォームが正しく表示される', async ({ page }) => {
    await page.goto('/auth/login');
    
    // ログインフォームの要素が存在することを確認
    await expect(page.getByRole('heading', { name: /ログイン/i })).toBeVisible();
    await expect(page.getByLabel('メールアドレス')).toBeVisible();
    await expect(page.getByLabel('パスワード')).toBeVisible();
    await expect(page.getByRole('button', { name: /ログイン/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /Googleでログイン/i })).toBeVisible();
  });

  test('空のフォームでログインしようとするとエラーが表示される', async ({ page }) => {
    await page.goto('/auth/login');
    
    // ログインボタンをクリック
    await page.getByRole('button', { name: /ログイン/i }).click();
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/メールアドレスを入力してください/i)).toBeVisible();
    await expect(page.getByText(/パスワードを入力してください/i)).toBeVisible();
  });

  test('無効なメールアドレスでエラーが表示される', async ({ page }) => {
    await page.goto('/auth/login');
    
    // 無効なメールアドレスを入力
    await page.getByLabel('メールアドレス').fill('invalid-email');
    await page.getByLabel('パスワード').fill('password123');
    await page.getByRole('button', { name: /ログイン/i }).click();
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/有効なメールアドレスを入力してください/i)).toBeVisible();
  });

  test('登録ページへのリンクが機能する', async ({ page }) => {
    await page.goto('/auth/login');
    
    // 登録リンクをクリック
    await page.getByRole('link', { name: /アカウントを作成/i }).click();
    
    // 登録ページに遷移することを確認
    await expect(page).toHaveURL(/\/auth\/register/);
    await expect(page.getByRole('heading', { name: /アカウント作成/i })).toBeVisible();
  });

  test('Googleログインボタンが機能する', async ({ page, context }) => {
    await page.goto('/auth/login');
    
    // 新しいページのプロミスを作成（OAuth認証ウィンドウ用）
    const pagePromise = context.waitForEvent('page');
    
    // Googleログインボタンをクリック
    await page.getByRole('button', { name: /Googleでログイン/i }).click();
    
    // 新しいウィンドウが開くことを確認
    const newPage = await pagePromise;
    
    // GoogleのOAuth URLに遷移することを確認
    await expect(newPage).toHaveURL(/accounts\.google\.com/);
  });
});

test.describe('登録フロー', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/register');
  });

  test('登録フォームが正しく表示される', async ({ page }) => {
    // 登録フォームの要素が存在することを確認
    await expect(page.getByRole('heading', { name: /アカウント作成/i })).toBeVisible();
    await expect(page.getByLabel('お名前')).toBeVisible();
    await expect(page.getByLabel('メールアドレス')).toBeVisible();
    await expect(page.getByLabel('パスワード')).toBeVisible();
    await expect(page.getByLabel('パスワード（確認）')).toBeVisible();
    await expect(page.getByRole('button', { name: /登録/i })).toBeVisible();
  });

  test('パスワードが一致しない場合エラーが表示される', async ({ page }) => {
    // フォームに入力
    await page.getByLabel('お名前').fill('テストユーザー');
    await page.getByLabel('メールアドレス').fill('test@example.com');
    await page.getByLabel('パスワード').fill('password123');
    await page.getByLabel('パスワード（確認）').fill('password456');
    
    // 登録ボタンをクリック
    await page.getByRole('button', { name: /登録/i }).click();
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/パスワードが一致しません/i)).toBeVisible();
  });

  test('弱いパスワードでエラーが表示される', async ({ page }) => {
    // フォームに入力
    await page.getByLabel('お名前').fill('テストユーザー');
    await page.getByLabel('メールアドレス').fill('test@example.com');
    await page.getByLabel('パスワード').fill('123');
    await page.getByLabel('パスワード（確認）').fill('123');
    
    // 登録ボタンをクリック
    await page.getByRole('button', { name: /登録/i }).click();
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/パスワードは8文字以上で入力してください/i)).toBeVisible();
  });
});

test.describe('認証状態の保持', () => {
  test('ログイン後、リロードしても認証状態が保持される', async ({ page, context }) => {
    // モックトークンをlocalStorageに設定
    await context.addInitScript(() => {
      window.localStorage.setItem('oauth_tokens', JSON.stringify({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        expires_at: Date.now() + 3600000, // 1時間後
        token_type: 'Bearer'
      }));
    });
    
    // ダッシュボードに移動
    await page.goto('/dashboard');
    
    // ログインページにリダイレクトされないことを確認
    await expect(page).not.toHaveURL(/\/auth\/login/);
    
    // ページをリロード
    await page.reload();
    
    // まだダッシュボードにいることを確認
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('トークンが期限切れの場合、ログインページにリダイレクトされる', async ({ page, context }) => {
    // 期限切れのモックトークンをlocalStorageに設定
    await context.addInitScript(() => {
      window.localStorage.setItem('oauth_tokens', JSON.stringify({
        access_token: 'expired_token',
        refresh_token: 'expired_refresh_token',
        expires_at: Date.now() - 1000, // 1秒前に期限切れ
        token_type: 'Bearer'
      }));
    });
    
    // ダッシュボードに移動
    await page.goto('/dashboard');
    
    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('ログアウトボタンが機能する', async ({ page, context }) => {
    // モックトークンをlocalStorageに設定
    await context.addInitScript(() => {
      window.localStorage.setItem('oauth_tokens', JSON.stringify({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        expires_at: Date.now() + 3600000,
        token_type: 'Bearer'
      }));
    });
    
    // ダッシュボードに移動
    await page.goto('/dashboard');
    
    // ログアウトボタンをクリック
    await page.getByRole('button', { name: /ログアウト/i }).click();
    
    // ログインページにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/auth\/login/);
    
    // localStorageからトークンが削除されていることを確認
    const tokens = await page.evaluate(() => {
      return window.localStorage.getItem('oauth_tokens');
    });
    expect(tokens).toBeNull();
  });
});

test.describe('OAuth認証フロー', () => {
  test('OAuth認証成功後、正しくリダイレクトされる', async ({ page, context }) => {
    // OAuthコールバックページに移動（成功パラメータ付き）
    await page.goto('/auth/callback?code=test_auth_code&state=test_state');
    
    // 処理中のメッセージが表示されることを確認
    await expect(page.getByText(/認証処理中/i)).toBeVisible();
    
    // APIレスポンスをモック
    await page.route('**/api/v1/auth/google/callback*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
          token_type: 'bearer',
          expires_in: 3600
        })
      });
    });
    
    // ダッシュボードにリダイレクトされることを確認
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  });

  test('OAuth認証エラー時、エラーメッセージが表示される', async ({ page }) => {
    // OAuthコールバックページに移動（エラーパラメータ付き）
    await page.goto('/auth/callback?error=access_denied&error_description=User%20denied%20access');
    
    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/認証エラー/i)).toBeVisible();
    await expect(page.getByText(/User denied access/i)).toBeVisible();
    
    // ログインページへのリンクが表示されることを確認
    await expect(page.getByRole('link', { name: /ログインページに戻る/i })).toBeVisible();
  });
});