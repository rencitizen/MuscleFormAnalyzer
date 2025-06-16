#!/usr/bin/env node

/**
 * OAuth Setup Verification Script
 * Run this script to verify your Firebase and Google OAuth configuration
 * Usage: node scripts/verify-oauth-setup.js
 */

const chalk = require('chalk');

// Colorize output
const log = {
  success: (msg) => console.log(chalk.green('✓'), msg),
  error: (msg) => console.log(chalk.red('✗'), msg),
  warning: (msg) => console.log(chalk.yellow('⚠'), msg),
  info: (msg) => console.log(chalk.blue('ℹ'), msg),
  section: (msg) => console.log(chalk.bold.cyan(`\n${msg}\n${'='.repeat(msg.length)}`))
};

// Check if environment variables are loaded
function checkEnvironmentVariables() {
  log.section('環境変数チェック');
  
  const requiredVars = [
    'NEXT_PUBLIC_FIREBASE_API_KEY',
    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
    'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
    'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
    'NEXT_PUBLIC_FIREBASE_APP_ID'
  ];
  
  let allVarsSet = true;
  
  requiredVars.forEach(varName => {
    const value = process.env[varName];
    if (value) {
      log.success(`${varName}: ${value.substring(0, 20)}...`);
    } else {
      log.error(`${varName}: 未設定`);
      allVarsSet = false;
    }
  });
  
  return allVarsSet;
}

// Generate configuration report
function generateConfigReport() {
  log.section('設定レポート');
  
  const authDomain = process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN;
  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;
  
  if (authDomain && projectId) {
    log.info(`Firebase Auth Domain: ${authDomain}`);
    log.info(`Firebase Project ID: ${projectId}`);
    log.info(`Firebase Console: https://console.firebase.google.com/project/${projectId}`);
    log.info(`Google Cloud Console: https://console.cloud.google.com/home/dashboard?project=${projectId}`);
  }
}

// Generate setup checklist
function generateChecklist(deploymentUrl) {
  log.section('セットアップチェックリスト');
  
  const steps = [
    {
      title: 'Firebase Console設定',
      items: [
        `Firebase Console (https://console.firebase.google.com) にアクセス`,
        `Authentication → Settings → Authorized domains を開く`,
        `以下のドメインが追加されているか確認:`,
        `  - localhost`,
        `  - ${deploymentUrl || 'your-app.vercel.app'}`
      ]
    },
    {
      title: 'Google Cloud Console設定',
      items: [
        `Google Cloud Console (https://console.cloud.google.com) にアクセス`,
        `APIs & Services → Credentials → OAuth 2.0 Client IDs を開く`,
        `Web client を編集`,
        `Authorized JavaScript origins に以下が含まれているか確認:`,
        `  - http://localhost:3000`,
        `  - https://${deploymentUrl || 'your-app.vercel.app'}`,
        `Authorized redirect URIs に以下が含まれているか確認:`,
        `  - http://localhost:3000/__/auth/handler`,
        `  - https://${deploymentUrl || 'your-app.vercel.app'}/__/auth/handler`
      ]
    },
    {
      title: 'Vercel設定',
      items: [
        `Vercel Dashboard (https://vercel.com) にアクセス`,
        `Project Settings → Environment Variables を確認`,
        `すべてのFirebase環境変数が設定されているか確認`,
        `Production環境用の変数が設定されているか確認`
      ]
    }
  ];
  
  steps.forEach(step => {
    console.log(chalk.bold(`\n${step.title}:`));
    step.items.forEach(item => {
      console.log(`  [ ] ${item}`);
    });
  });
}

// Generate debug URLs
function generateDebugUrls(deploymentUrl) {
  log.section('デバッグ用URL');
  
  const urls = {
    'ローカル開発': 'http://localhost:3000',
    'Vercelプレビュー': `https://${deploymentUrl || 'your-app.vercel.app'}`,
    'テスト用リダイレクトURI': `https://${deploymentUrl || 'your-app.vercel.app'}/__/auth/handler`
  };
  
  Object.entries(urls).forEach(([label, url]) => {
    log.info(`${label}: ${url}`);
  });
}

// Main execution
function main() {
  console.log(chalk.bold.magenta(`
╔═══════════════════════════════════════╗
║     OAuth Setup Verification Tool     ║
╚═══════════════════════════════════════╝
  `));
  
  // Get deployment URL from command line argument
  const deploymentUrl = process.argv[2];
  
  if (deploymentUrl) {
    log.info(`デプロイメントURL: ${deploymentUrl}`);
  } else {
    log.warning('使用方法: node scripts/verify-oauth-setup.js [your-deployment-url]');
    log.warning('例: node scripts/verify-oauth-setup.js muscle-form-analyzer-c5ukwtnbq.vercel.app');
  }
  
  // Load environment variables from .env.local
  try {
    require('dotenv').config({ path: '.env.local' });
  } catch (e) {
    log.warning('.env.localファイルが見つかりません');
  }
  
  // Run checks
  const envVarsOk = checkEnvironmentVariables();
  generateConfigReport();
  generateChecklist(deploymentUrl);
  generateDebugUrls(deploymentUrl);
  
  // Summary
  log.section('サマリー');
  
  if (envVarsOk) {
    log.success('環境変数はすべて設定されています');
  } else {
    log.error('必要な環境変数が不足しています');
    log.info('Vercel Dashboardで環境変数を設定してください');
  }
  
  log.info('\n次のステップ:');
  log.info('1. 上記のチェックリストを確認');
  log.info('2. 必要な設定を追加');
  log.info('3. 5-10分待機（設定反映のため）');
  log.info('4. ブラウザのキャッシュをクリア');
  log.info('5. シークレットモードでテスト');
  
  console.log(chalk.gray('\n問題が解決しない場合は、frontend/components/auth/OAuthDebugPanel.tsx を使用してください'));
}

// Check if chalk is installed
try {
  require.resolve('chalk');
  main();
} catch (e) {
  console.log('Installing required dependencies...');
  require('child_process').execSync('npm install chalk dotenv', { stdio: 'inherit' });
  console.log('Dependencies installed. Please run the script again.');
}