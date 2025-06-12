import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'
import { env } from './config/env'

// Use the centralized environment configuration
const firebaseConfig = env.firebase

// Debug logging only in development
if (env.isDevelopment && typeof window !== 'undefined') {
  console.log('🔍 Firebase Config Debug:')
  console.log('Environment:', process.env.NODE_ENV)
  console.log('Project ID:', firebaseConfig.projectId)
  console.log('Auth Domain:', firebaseConfig.authDomain)
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