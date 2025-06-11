import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

// デバッグ用：環境変数の確認
if (typeof window !== 'undefined') {
  console.log('Firebase Config Debug:')
  console.log('API Key:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY)
  console.log('Auth Domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN)
  console.log('Project ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID)
  console.log('Storage Bucket:', process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET)
  console.log('Messaging Sender ID:', process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID)
  console.log('App ID:', process.env.NEXT_PUBLIC_FIREBASE_APP_ID)
}

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
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