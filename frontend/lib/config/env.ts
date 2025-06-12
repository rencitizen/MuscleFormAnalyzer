// Centralized environment configuration with validation
// This provides type-safe access to environment variables with proper defaults

interface FirebaseConfig {
  apiKey: string
  authDomain: string
  projectId: string
  storageBucket: string
  messagingSenderId: string
  appId: string
}

interface EnvironmentConfig {
  firebase: FirebaseConfig
  isProduction: boolean
  isDevelopment: boolean
  isVercel: boolean
}

// Default Firebase configuration for development/demo
const DEFAULT_FIREBASE_CONFIG: FirebaseConfig = {
  apiKey: 'demo-api-key',
  authDomain: 'demo.firebaseapp.com',
  projectId: 'demo-project',
  storageBucket: 'demo-project.appspot.com',
  messagingSenderId: '123456789',
  appId: '1:123456789:web:abcdef'
}

// Validate and get Firebase configuration
function getFirebaseConfig(): FirebaseConfig {
  // In production (Vercel), require all Firebase env vars
  const isVercel = process.env.VERCEL === '1'
  
  if (isVercel && process.env.NODE_ENV === 'production') {
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
      console.error('Missing required Firebase environment variables:', missingVars)
      console.warn('Using default Firebase configuration. Authentication features may not work properly.')
      console.warn('Please add these variables in Vercel Dashboard > Settings > Environment Variables')
      return DEFAULT_FIREBASE_CONFIG
    }
  }
  
  // Return actual config if available, otherwise defaults
  return {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || DEFAULT_FIREBASE_CONFIG.apiKey,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || DEFAULT_FIREBASE_CONFIG.authDomain,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || DEFAULT_FIREBASE_CONFIG.projectId,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || DEFAULT_FIREBASE_CONFIG.storageBucket,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || DEFAULT_FIREBASE_CONFIG.messagingSenderId,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || DEFAULT_FIREBASE_CONFIG.appId
  }
}

// Export the configuration object
export const env: EnvironmentConfig = {
  firebase: getFirebaseConfig(),
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development',
  isVercel: process.env.VERCEL === '1'
}

// Log configuration status (only in development)
if (env.isDevelopment) {
  console.log('Environment Configuration:', {
    environment: process.env.NODE_ENV,
    isVercel: env.isVercel,
    firebaseProjectId: env.firebase.projectId
  })
}