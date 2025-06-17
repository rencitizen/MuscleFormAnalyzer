#!/usr/bin/env node

/**
 * Google OAuth認証の設定確認スクリプト
 * 使用方法: node scripts/check-google-auth.js
 */

const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// 色付きコンソール出力
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

const log = {
  error: (msg) => console.log(`${colors.red}✗ ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✓ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}! ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.blue}ℹ ${msg}${colors.reset}`),
  header: (msg) => console.log(`\n${colors.cyan}=== ${msg} ===${colors.reset}\n`),
};

// .env.localファイルを読み込む
const envPath = path.join(__dirname, '../.env.local');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
} else {
  log.error('.env.local ファイルが見つかりません');
  log.info('.env.example を .env.local にコピーして設定してください:');
  console.log('  cp .env.example .env.local');
  process.exit(1);
}

// 必須環境変数のチェック
log.header('環境変数チェック');

const requiredEnvVars = {
  'NEXTAUTH_URL': {
    description: 'NextAuth.js用のベースURL',
    example: 'http://localhost:3000',
  },
  'NEXTAUTH_SECRET': {
    description: 'NextAuth.js用のシークレットキー',
    example: 'openssl rand -base64 32 で生成',
  },
  'GOOGLE_CLIENT_ID': {
    description: 'Google OAuth Client ID',
    example: 'xxxxx.apps.googleusercontent.com',
  },
  'GOOGLE_CLIENT_SECRET': {
    description: 'Google OAuth Client Secret',
    example: 'GOCSPX-xxxxx',
  },
};

let hasErrors = false;

Object.entries(requiredEnvVars).forEach(([key, info]) => {
  const value = process.env[key];
  if (!value) {
    log.error(`${key} が設定されていません`);
    console.log(`  説明: ${info.description}`);
    console.log(`  例: ${info.example}`);
    hasErrors = true;
  } else {
    log.success(`${key} は設定済み`);
  }
});

// Redirect URIの生成
log.header('Redirect URI 設定');

const baseUrl = process.env.NEXTAUTH_URL || 'http://localhost:3000';
const redirectUris = [
  `${baseUrl}/api/auth/callback/google`,
  `${baseUrl}/__/auth/handler`,
  `${baseUrl}/auth/callback`,
];

console.log('Google Cloud Console に以下のURIを追加してください:\n');
console.log(`${colors.magenta}Authorized JavaScript origins:${colors.reset}`);
console.log(`  - ${baseUrl}`);

console.log(`\n${colors.magenta}Authorized redirect URIs:${colors.reset}`);
redirectUris.forEach(uri => {
  console.log(`  - ${uri}`);
});

// Vercel環境の追加URI
if (process.env.VERCEL_URL) {
  const vercelUrl = `https://${process.env.VERCEL_URL}`;
  console.log(`\n${colors.yellow}Vercel環境用の追加URI:${colors.reset}`);
  console.log(`  - ${vercelUrl}`);
  console.log(`  - ${vercelUrl}/api/auth/callback/google`);
  console.log(`  - ${vercelUrl}/__/auth/handler`);
  console.log(`  - ${vercelUrl}/auth/callback`);
}

// 設定手順
log.header('設定手順');

console.log('1. Google Cloud Console にアクセス:');
console.log(`   ${colors.blue}https://console.cloud.google.com/apis/credentials${colors.reset}`);
console.log('\n2. OAuth 2.0 クライアントIDを選択');
console.log('\n3. 上記のURIを追加:');
console.log('   - Authorized JavaScript origins にベースURLを追加');
console.log('   - Authorized redirect URIs に完全なパスを追加');
console.log('\n4. 保存して5-10分待つ（変更が反映されるまで）');

// Firebase設定の確認
log.header('Firebase設定（オプション）');

const firebaseVars = [
  'NEXT_PUBLIC_FIREBASE_API_KEY',
  'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
  'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
];

let hasFirebase = true;
firebaseVars.forEach(key => {
  if (!process.env[key]) {
    hasFirebase = false;
  }
});

if (hasFirebase) {
  log.success('Firebase設定は完了しています');
  console.log('\nFirebase Consoleでも以下を確認してください:');
  console.log('1. Authentication > Sign-in method > Google が有効');
  console.log('2. Authentication > Settings > Authorized domains にドメインを追加');
} else {
  log.warning('Firebase設定が不完全です（Firebase認証を使用しない場合は無視してください）');
}

// 最終確認
log.header('診断結果');

if (hasErrors) {
  log.error('必須の環境変数が設定されていません');
  console.log('\n.env.local ファイルを編集して、必要な値を設定してください');
  process.exit(1);
} else {
  log.success('環境変数の設定は完了しています');
  console.log('\nGoogle Cloud Console でRedirect URIを設定してください');
  console.log('設定後、アプリケーションを再起動してください:');
  console.log(`  ${colors.cyan}npm run dev${colors.reset}`);
}

// デバッグ用のコマンド
console.log(`\n${colors.yellow}デバッグ用コマンド:${colors.reset}`);
console.log('ブラウザのコンソールで以下を実行:');
console.log('  googleAuthDebugger.displayDebugInfo()');
console.log('  googleAuthDebugger.diagnoseError(error)');