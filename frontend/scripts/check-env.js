#!/usr/bin/env node

// Environment Variables Check Script for Vercel
// This script runs during the build process to validate environment variables

console.log('=== Environment Variables Check ===')  
console.log('NODE_ENV:', process.env.NODE_ENV)
console.log('Build Environment:', process.env.VERCEL ? 'Vercel' : 'Local')
console.log('')

const requiredEnvVars = [
  'NEXT_PUBLIC_FIREBASE_API_KEY',
  'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
  'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
  'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
  'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
  'NEXT_PUBLIC_FIREBASE_APP_ID'
]

let missingVars = []

console.log('Checking required environment variables:')
requiredEnvVars.forEach(varName => {
  const value = process.env[varName]
  if (value) {
    console.log(`✅ ${varName}: ${value.substring(0, 10)}...`)
  } else {
    console.log(`❌ ${varName}: NOT FOUND`)
    missingVars.push(varName)
  }
})

console.log('')
console.log('All NEXT_PUBLIC_ variables:')
Object.keys(process.env)
  .filter(key => key.startsWith('NEXT_PUBLIC_'))
  .forEach(key => {
    console.log(`  ${key}: ${process.env[key]?.substring(0, 20)}...`)
  })

// On Vercel, only warn about missing vars, don't fail the build
if (missingVars.length > 0) {
  console.log('')
  console.log('⚠️  Warning: Missing environment variables:', missingVars.join(', '))
  if (process.env.VERCEL) {
    console.log('⚠️  Running on Vercel - continuing with build despite missing variables')
    console.log('⚠️  Make sure to add these variables in Vercel Dashboard > Settings > Environment Variables')
    process.exit(0) // Exit successfully on Vercel
  } else {
    console.log('❌ Local build - please set up environment variables')
    // Don't fail on local either to allow development
    process.exit(0)
  }
}

console.log('')
console.log('✅ Environment check completed successfully!')
process.exit(0)