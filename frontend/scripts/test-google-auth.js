#!/usr/bin/env node

/**
 * Google認証設定テストスクリプト
 * Firebase設定とGoogle OAuth設定の検証を行います
 */

const chalk = require('chalk');

console.log(chalk.blue('\n🔍 Google認証設定テスト開始...\n'));

// 環境変数チェック
console.log(chalk.yellow('1. 環境変数チェック:'));
const requiredEnvVars = [
  'NEXT_PUBLIC_FIREBASE_API_KEY',
  'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
  'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
  'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
  'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
  'NEXT_PUBLIC_FIREBASE_APP_ID'
];

let envVarsOk = true;
requiredEnvVars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    console.log(chalk.green(`  ✓ ${varName}: ${value.substring(0, 10)}...`));
  } else {
    console.log(chalk.red(`  ✗ ${varName}: 未設定`));
    envVarsOk = false;
  }
});

// Auth Domain形式チェック
console.log(chalk.yellow('\n2. Auth Domain形式チェック:'));
const authDomain = process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN;
if (authDomain) {
  if (authDomain.endsWith('.firebaseapp.com')) {
    console.log(chalk.green(`  ✓ 正しい形式: ${authDomain}`));
  } else {
    console.log(chalk.red(`  ✗ 不正な形式: ${authDomain}`));
    console.log(chalk.gray('    期待される形式: [project-id].firebaseapp.com'));
  }
} else {
  console.log(chalk.red('  ✗ AUTH_DOMAINが未設定'));
}

// 設定ファイルチェック
console.log(chalk.yellow('\n3. 設定ファイルチェック:'));
const fs = require('fs');
const path = require('path');

const filesToCheck = [
  'lib/config/env.ts',
  'lib/firebase.ts',
  'components/providers/AuthProvider.tsx',
  'app/auth/callback/page.tsx',
  'public/manifest.json'
];

filesToCheck.forEach(file => {
  const filePath = path.join(__dirname, '..', file);
  if (fs.existsSync(filePath)) {
    console.log(chalk.green(`  ✓ ${file}`));
  } else {
    console.log(chalk.red(`  ✗ ${file} が見つかりません`));
  }
});

// PWAメタタグチェック
console.log(chalk.yellow('\n4. PWAメタタグチェック:'));
const layoutPath = path.join(__dirname, '..', 'app/layout.tsx');
if (fs.existsSync(layoutPath)) {
  const layoutContent = fs.readFileSync(layoutPath, 'utf8');
  const pwaTags = [
    'apple-mobile-web-app-capable',
    'apple-mobile-web-app-status-bar-style',
    'mobile-web-app-capable',
    'format-detection'
  ];
  
  pwaTags.forEach(tag => {
    if (layoutContent.includes(tag)) {
      console.log(chalk.green(`  ✓ ${tag}`));
    } else {
      console.log(chalk.red(`  ✗ ${tag} が見つかりません`));
    }
  });
}

// manifest.json検証
console.log(chalk.yellow('\n5. manifest.json検証:'));
const manifestPath = path.join(__dirname, '..', 'public/manifest.json');
if (fs.existsSync(manifestPath)) {
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    const requiredFields = ['name', 'short_name', 'start_url', 'display', 'icons'];
    
    requiredFields.forEach(field => {
      if (manifest[field]) {
        console.log(chalk.green(`  ✓ ${field}: ${typeof manifest[field] === 'object' ? 'OK' : manifest[field]}`));
      } else {
        console.log(chalk.red(`  ✗ ${field} が未定義`));
      }
    });
  } catch (error) {
    console.log(chalk.red('  ✗ manifest.jsonの解析エラー'));
  }
}

// チェックリスト表示
console.log(chalk.yellow('\n📋 手動確認チェックリスト:'));
console.log(chalk.white(`
1. Firebase Console設定:
   ${chalk.gray('https://console.firebase.google.com')}
   □ Authentication → Sign-in method → Google 有効化
   □ Authentication → Settings → Authorized domains に追加:
     - muscle-form-analyzer.vercel.app
     - localhost

2. Google Cloud Console設定:
   ${chalk.gray('https://console.cloud.google.com')}
   □ APIs & Services → Credentials → OAuth 2.0 Client IDs 設定
   □ Authorized JavaScript origins:
     - https://muscle-form-analyzer.vercel.app
     - http://localhost:3000
   □ Authorized redirect URIs:
     - https://muscle-form-analyzer.vercel.app/__/auth/handler
     - http://localhost:3000/__/auth/handler

3. Vercel設定:
   ${chalk.gray('https://vercel.com/dashboard')}
   □ Settings → Environment Variables で全ての環境変数設定

4. ローカルテスト:
   □ npm run dev でローカル起動
   □ Googleログインボタンクリック
   □ エラーメッセージ確認
`));

// 結果サマリー
console.log(chalk.blue('\n📊 テスト結果サマリー:'));
if (envVarsOk) {
  console.log(chalk.green('  ✓ 環境変数: OK'));
} else {
  console.log(chalk.red('  ✗ 環境変数: 不足あり'));
}

console.log(chalk.gray('\n次のステップ:'));
console.log(chalk.white('1. 上記のチェックリストを確認'));
console.log(chalk.white('2. git add . && git commit -m "Fix Google login" && git push'));
console.log(chalk.white('3. Vercelでデプロイ完了を待つ'));
console.log(chalk.white('4. 本番環境でGoogleログインをテスト\n'));