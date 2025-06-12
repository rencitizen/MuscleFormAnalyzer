#!/usr/bin/env node

/**
 * Googleログイン設定のライブチェックスクリプト
 * 本番環境の設定状態を確認します
 */

const https = require('https');
const chalk = require('chalk');

console.log(chalk.blue('\n🔍 Googleログイン設定ライブチェック開始...\n'));

// 本番URLの設定
const PRODUCTION_URL = 'https://muscle-form-analyzer.vercel.app';

// HTTPSリクエストを実行する関数
function checkUrl(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve({ statusCode: res.statusCode, data }));
    }).on('error', reject);
  });
}

async function runChecks() {
  // 1. 本番サイトの到達確認
  console.log(chalk.yellow('1. 本番サイトの到達確認:'));
  try {
    const siteCheck = await checkUrl(PRODUCTION_URL);
    if (siteCheck.statusCode === 200) {
      console.log(chalk.green(`  ✓ サイトは正常に動作しています (Status: ${siteCheck.statusCode})`));
    } else {
      console.log(chalk.red(`  ✗ サイトにアクセスできません (Status: ${siteCheck.statusCode})`));
    }
  } catch (error) {
    console.log(chalk.red(`  ✗ サイトへの接続エラー: ${error.message}`));
  }

  // 2. manifest.jsonの確認
  console.log(chalk.yellow('\n2. PWA設定 (manifest.json) の確認:'));
  try {
    const manifestCheck = await checkUrl(`${PRODUCTION_URL}/manifest.json`);
    if (manifestCheck.statusCode === 200) {
      console.log(chalk.green('  ✓ manifest.jsonは正常にアクセス可能'));
      const manifest = JSON.parse(manifestCheck.data);
      console.log(chalk.gray(`    - name: ${manifest.name}`));
      console.log(chalk.gray(`    - short_name: ${manifest.short_name}`));
      console.log(chalk.gray(`    - icons: ${manifest.icons.length}個定義済み`));
    } else {
      console.log(chalk.red('  ✗ manifest.jsonにアクセスできません'));
    }
  } catch (error) {
    console.log(chalk.red(`  ✗ manifest.jsonの取得エラー: ${error.message}`));
  }

  // 3. 認証ページの確認
  console.log(chalk.yellow('\n3. 認証ページの確認:'));
  const authPages = ['/auth/login', '/auth/register', '/auth/callback'];
  
  for (const page of authPages) {
    try {
      const pageCheck = await checkUrl(`${PRODUCTION_URL}${page}`);
      if (pageCheck.statusCode === 200) {
        console.log(chalk.green(`  ✓ ${page} は正常にアクセス可能`));
      } else {
        console.log(chalk.red(`  ✗ ${page} にアクセスできません (Status: ${pageCheck.statusCode})`));
      }
    } catch (error) {
      console.log(chalk.red(`  ✗ ${page} の取得エラー: ${error.message}`));
    }
  }

  // チェック手順の表示
  console.log(chalk.yellow('\n📋 手動確認手順:\n'));
  
  console.log(chalk.white('1. ブラウザでの確認:'));
  console.log(chalk.gray(`   - ${PRODUCTION_URL}/auth/login にアクセス`));
  console.log(chalk.gray('   - F12で開発者ツールを開く'));
  console.log(chalk.gray('   - Consoleタブでエラーメッセージを確認'));
  console.log(chalk.gray('   - Networkタブで失敗したリクエストを確認'));
  
  console.log(chalk.white('\n2. Googleログインボタンのテスト:'));
  console.log(chalk.gray('   - Googleログインボタンをクリック'));
  console.log(chalk.gray('   - ポップアップまたはリダイレクトが発生するか確認'));
  console.log(chalk.gray('   - エラーメッセージの内容をメモ'));
  
  console.log(chalk.white('\n3. よくあるエラーメッセージ:'));
  console.log(chalk.gray('   - "auth/unauthorized-domain" → Firebase Consoleでドメイン追加'));
  console.log(chalk.gray('   - "auth/configuration-not-found" → Vercel環境変数確認'));
  console.log(chalk.gray('   - "auth/operation-not-allowed" → Firebase ConsoleでGoogle認証有効化'));
  console.log(chalk.gray('   - "popup blocked" → 自動的にリダイレクト方式に切り替わるはず'));
  
  console.log(chalk.blue('\n🔧 トラブルシューティング:\n'));
  
  console.log(chalk.white('Firebase Console確認:'));
  console.log(chalk.gray('1. https://console.firebase.google.com'));
  console.log(chalk.gray('2. Authentication → Sign-in method → Google が有効か'));
  console.log(chalk.gray('3. Authentication → Settings → Authorized domains に'));
  console.log(chalk.gray(`   - ${PRODUCTION_URL.replace('https://', '')} が追加されているか`));
  
  console.log(chalk.white('\nGoogle Cloud Console確認:'));
  console.log(chalk.gray('1. https://console.cloud.google.com'));
  console.log(chalk.gray('2. APIs & Services → Credentials'));
  console.log(chalk.gray('3. OAuth 2.0 Client IDs → Web client を編集'));
  console.log(chalk.gray('4. Authorized JavaScript origins に追加:'));
  console.log(chalk.gray(`   - ${PRODUCTION_URL}`));
  console.log(chalk.gray('5. Authorized redirect URIs に追加:'));
  console.log(chalk.gray(`   - ${PRODUCTION_URL}/__/auth/handler`));
  
  console.log(chalk.white('\nVercel環境変数確認:'));
  console.log(chalk.gray('1. https://vercel.com/dashboard'));
  console.log(chalk.gray('2. Settings → Environment Variables'));
  console.log(chalk.gray('3. 以下の変数がすべて設定されているか:'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_API_KEY'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_PROJECT_ID'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID'));
  console.log(chalk.gray('   - NEXT_PUBLIC_FIREBASE_APP_ID'));
  
  console.log(chalk.green('\n✅ チェック完了!\n'));
}

// 実行
runChecks().catch(console.error);