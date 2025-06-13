#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('=== Google OAuth Error 400 診断ツール ===\n');

// 1. 環境変数チェック
console.log('1. 環境変数チェック:');
const envPath = path.join(__dirname, '../.env.local');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  const lines = envContent.split('\n');
  const firebaseVars = lines.filter(line => line.includes('FIREBASE'));
  
  console.log('✓ Firebase設定が見つかりました:');
  firebaseVars.forEach(line => {
    if (line.trim() && !line.startsWith('#')) {
      const [key] = line.split('=');
      console.log(`  - ${key}`);
    }
  });
  
  // Firebase Auth Domain確認
  const authDomainLine = lines.find(line => line.includes('FIREBASE_AUTH_DOMAIN'));
  if (authDomainLine) {
    const authDomain = authDomainLine.split('=')[1];
    console.log(`\n✓ Auth Domain: ${authDomain}`);
  }
} else {
  console.log('✗ .env.localファイルが見つかりません');
}

// 2. Vercelデプロイ情報
console.log('\n2. Vercelデプロイメント設定:');
console.log('以下のドメインを設定する必要があります:');
console.log('  - localhost (開発環境)');
console.log('  - *.vercel.app (プレビュー環境)');
console.log('  - あなたのカスタムドメイン (本番環境)');

// 3. 必要な設定手順
console.log('\n3. Google OAuth Error 400 修正手順:\n');

console.log('【Firebase Console での設定】');
console.log('1. https://console.firebase.google.com/');
console.log('2. プロジェクト "tenaxauth" を選択');
console.log('3. Authentication → Settings → Authorized domains');
console.log('4. 以下のドメインを追加:');
console.log('   - localhost');
console.log('   - *.vercel.app');
console.log('   - あなたのVercelデプロイURL');
console.log('');

console.log('【Google Cloud Console での設定】');
console.log('1. https://console.cloud.google.com/');
console.log('2. プロジェクト "tenaxauth" を選択');
console.log('3. APIs & Services → Credentials');
console.log('4. OAuth 2.0 Client IDsから既存のWeb clientを編集');
console.log('5. Authorized JavaScript origins に追加:');
console.log('   - http://localhost:3000');
console.log('   - https://localhost:3000');
console.log('   - https://[your-app-name].vercel.app');
console.log('   - https://[your-custom-domain]');
console.log('6. Authorized redirect URIs に追加:');
console.log('   - http://localhost:3000/__/auth/handler');
console.log('   - https://localhost:3000/__/auth/handler');
console.log('   - https://[your-app-name].vercel.app/__/auth/handler');
console.log('   - https://[your-custom-domain]/__/auth/handler');
console.log('');

console.log('【Vercel環境変数の設定】');
console.log('1. https://vercel.com/dashboard');
console.log('2. プロジェクトを選択 → Settings → Environment Variables');
console.log('3. 以下の環境変数を設定:');
console.log('   - NEXT_PUBLIC_FIREBASE_API_KEY');
console.log('   - NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN');
console.log('   - NEXT_PUBLIC_FIREBASE_PROJECT_ID');
console.log('   - NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET');
console.log('   - NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID');
console.log('   - NEXT_PUBLIC_FIREBASE_APP_ID');
console.log('');

console.log('【デバッグ用コード】');
console.log('エラーが発生した場合、ブラウザコンソールで以下を確認:');
console.log('- Current domain: エラーが発生しているドメイン');
console.log('- Auth domain: Firebase Auth Domain設定');
console.log('- Full URL: 現在のURL');
console.log('');

console.log('【一般的な原因】');
console.log('1. Authorized domainsにデプロイURLが追加されていない');
console.log('2. OAuth redirect URIsが正しく設定されていない');
console.log('3. Vercel環境変数が設定されていない');
console.log('4. Firebase Authenticationが有効化されていない');
console.log('5. Google Sign-in methodが有効化されていない');