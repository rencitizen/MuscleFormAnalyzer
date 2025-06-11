import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

// デバッグ用：環境変数の確認
console.log('🔍 Firebase Config Debug (Build time):')
console.log('NODE_ENV:', process.env.NODE_ENV)
console.log('API Key exists:', !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY)
console.log('API Key length:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.length || 0)
console.log('API Key value:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.substring(0, 10) + '...')

if (typeof window !== 'undefined') {
  console.log('🌐 Firebase Config Debug (Client side):')
  console.log('API Key:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY)
  console.log('Auth Domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN)
  console.log('Project ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID)
  console.log('Storage Bucket:', process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET)
  console.log('Messaging Sender ID:', process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID)
  console.log('App ID:', process.env.NEXT_PUBLIC_FIREBASE_APP_ID)
  
  // 全ての環境変数が存在するかチェック
  const requiredVars = [
    'NEXT_PUBLIC_FIREBASE_API_KEY',
    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
    'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
    'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
    'NEXT_PUBLIC_FIREBASE_APP_ID'
  ]
  
  const missingVars = requiredVars.filter(varName => !process.env[varName])
  if (missingVars.length > 0) {
    console.error('❌ Missing environment variables:', missingVars)
  } else {
    console.log('✅ All required environment variables are present')
  }
}

// Vercelで環境変数が読み込めない場合の一時的なフォールバック
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || 'AIzaSyAjfiJLZkNjx9kqdFdyew7Kno9NXUpGTXI',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'tenaxauth.firebaseapp.com',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'tenaxauth',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'tenaxauth.firebasestorage.app',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '957012960073',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || '1:957012960073:web:edf5449d38e087ab69f098'
}

// 環境変数が使われていない場合は警告
if (!process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
  console.warn('⚠️ Using hardcoded Firebase config. Please set environment variables in Vercel!')
}

// 設定の検証
if (!firebaseConfig.apiKey || firebaseConfig.apiKey === 'undefined') {
  console.error('Firebase API Key is missing or undefined!')
  console.error('Please check your environment variables in Vercel')
}

let app
let auth
let db
let storage

try {
  app = initializeApp(firebaseConfig)
  auth = getAuth(app)
  db = getFirestore(app)
  storage = getStorage(app)
  
  console.log('Firebase initialized successfully')
} catch (error) {
  console.error('Firebase initialization error:', error)
  console.error('Firebase config:', firebaseConfig)
  
  // エラー時でもエクスポートは必要
  auth = null as any
  db = null as any
  storage = null as any
}

export { auth, db, storage }
export default app