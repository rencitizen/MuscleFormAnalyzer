'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Camera, CheckCircle, XCircle, AlertCircle, Smartphone, Globe, Shield } from 'lucide-react'

interface DeviceInfo {
  deviceId: string
  groupId: string
  kind: string
  label: string
}

interface BrowserInfo {
  name: string
  version: string
  platform: string
  userAgent: string
}

export default function CameraTestComponent() {
  const [isHttps, setIsHttps] = useState(false)
  const [hasMediaDevices, setHasMediaDevices] = useState(false)
  const [hasGetUserMedia, setHasGetUserMedia] = useState(false)
  const [devices, setDevices] = useState<DeviceInfo[]>([])
  const [permissionStatus, setPermissionStatus] = useState<string>('unknown')
  const [browserInfo, setBrowserInfo] = useState<BrowserInfo | null>(null)
  const [testResult, setTestResult] = useState<'pending' | 'success' | 'failed'>('pending')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [stream, setStream] = useState<MediaStream | null>(null)

  useEffect(() => {
    // Check HTTPS
    const protocol = window.location.protocol
    setIsHttps(protocol === 'https:' || 
               window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1')

    // Check browser capabilities
    setHasMediaDevices(!!navigator.mediaDevices)
    setHasGetUserMedia(!!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia))

    // Get browser info
    const ua = navigator.userAgent
    let browserName = 'Unknown'
    let browserVersion = ''

    if (ua.includes('Chrome')) {
      browserName = 'Chrome'
      browserVersion = ua.match(/Chrome\/(\d+)/)?.[1] || ''
    } else if (ua.includes('Safari') && !ua.includes('Chrome')) {
      browserName = 'Safari'
      browserVersion = ua.match(/Version\/(\d+)/)?.[1] || ''
    } else if (ua.includes('Firefox')) {
      browserName = 'Firefox'
      browserVersion = ua.match(/Firefox\/(\d+)/)?.[1] || ''
    } else if (ua.includes('Edge')) {
      browserName = 'Edge'
      browserVersion = ua.match(/Edge\/(\d+)/)?.[1] || ''
    }

    setBrowserInfo({
      name: browserName,
      version: browserVersion,
      platform: navigator.platform,
      userAgent: ua
    })

    // Check camera permission
    checkCameraPermission()

    // Get devices
    getDeviceList()

    // Cleanup
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const checkCameraPermission = async () => {
    try {
      if ('permissions' in navigator) {
        const result = await navigator.permissions.query({ name: 'camera' as PermissionName })
        setPermissionStatus(result.state)
        
        result.addEventListener('change', () => {
          setPermissionStatus(result.state)
        })
      }
    } catch (err) {
      console.log('Permissions API not supported')
      setPermissionStatus('not-supported')
    }
  }

  const getDeviceList = async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = deviceList
        .filter(device => device.kind === 'videoinput')
        .map(device => ({
          deviceId: device.deviceId,
          groupId: device.groupId,
          kind: device.kind,
          label: device.label || `Camera ${device.deviceId.slice(0, 8)}...`
        }))
      setDevices(videoDevices)
    } catch (err) {
      console.error('Failed to enumerate devices:', err)
    }
  }

  const testCamera = async () => {
    setTestResult('pending')
    setErrorMessage('')

    try {
      // Stop any existing stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }

      // Try to get camera stream
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      })

      setStream(mediaStream)
      setTestResult('success')
      
      // Refresh device list with labels
      await getDeviceList()
      
      // Stop stream after 3 seconds
      setTimeout(() => {
        mediaStream.getTracks().forEach(track => track.stop())
        setStream(null)
      }, 3000)
    } catch (err: any) {
      setTestResult('failed')
      setErrorMessage(err.message || 'Unknown error')
      console.error('Camera test failed:', err)
    }
  }

  const getStatusIcon = (status: boolean) => {
    return status ? 
      <CheckCircle className="w-5 h-5 text-green-600" /> : 
      <XCircle className="w-5 h-5 text-red-600" />
  }

  const getPermissionBadge = (status: string) => {
    const variants: Record<string, any> = {
      'granted': { variant: 'default', className: 'bg-green-100 text-green-800' },
      'denied': { variant: 'destructive' },
      'prompt': { variant: 'secondary' },
      'unknown': { variant: 'outline' },
      'not-supported': { variant: 'outline' }
    }
    
    const config = variants[status] || variants['unknown']
    
    return (
      <Badge variant={config.variant} className={config.className}>
        {status}
      </Badge>
    )
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">カメラ機能診断</h1>
      
      <div className="space-y-6">
        {/* Environment Check */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              環境チェック
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span>HTTPS接続</span>
              <div className="flex items-center gap-2">
                {getStatusIcon(isHttps)}
                <span className="text-sm text-gray-600">
                  {window.location.protocol}//
                </span>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <span>MediaDevices API</span>
              {getStatusIcon(hasMediaDevices)}
            </div>
            
            <div className="flex items-center justify-between">
              <span>getUserMedia API</span>
              {getStatusIcon(hasGetUserMedia)}
            </div>
          </CardContent>
        </Card>

        {/* Browser Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="w-5 h-5" />
              ブラウザ情報
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {browserInfo && (
              <>
                <div className="flex items-center justify-between">
                  <span>ブラウザ</span>
                  <span className="font-mono">{browserInfo.name} {browserInfo.version}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>プラットフォーム</span>
                  <span className="font-mono">{browserInfo.platform}</span>
                </div>
                <div className="text-xs text-gray-500 mt-2 p-2 bg-gray-50 rounded break-all">
                  {browserInfo.userAgent}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Camera Permission */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              カメラ権限
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span>権限状態</span>
              {getPermissionBadge(permissionStatus)}
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>検出されたカメラ数</span>
                <Badge variant="outline">{devices.length}</Badge>
              </div>
              
              {devices.length > 0 && (
                <div className="mt-2 space-y-1">
                  {devices.map((device, index) => (
                    <div key={device.deviceId} className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                      <div className="font-medium">カメラ {index + 1}</div>
                      <div className="text-xs">
                        {device.label || 'Unknown Device'}
                      </div>
                      <div className="text-xs font-mono text-gray-400">
                        ID: {device.deviceId.slice(0, 16)}...
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Camera Test */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              カメラテスト
            </CardTitle>
            <CardDescription>
              実際にカメラにアクセスしてテストします
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={testCamera} 
              disabled={!isHttps || !hasGetUserMedia}
              className="w-full"
            >
              カメラテストを実行
            </Button>
            
            {testResult === 'success' && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  カメラアクセス成功！3秒後に自動的に停止します。
                </AlertDescription>
              </Alert>
            )}
            
            {testResult === 'failed' && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  カメラアクセス失敗: {errorMessage}
                </AlertDescription>
              </Alert>
            )}
            
            {stream && (
              <div className="mt-4 p-4 bg-green-50 rounded">
                <p className="text-sm text-green-800">
                  カメラストリーム: アクティブ
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Troubleshooting */}
        {(testResult === 'failed' || !isHttps || permissionStatus === 'denied') && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="mt-2">
              <h3 className="font-semibold mb-2">問題が検出されました</h3>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {!isHttps && (
                  <li>HTTPS接続ではありません。カメラアクセスにはHTTPSが必要です。</li>
                )}
                {permissionStatus === 'denied' && (
                  <li>カメラ権限が拒否されています。ブラウザの設定から許可してください。</li>
                )}
                {testResult === 'failed' && errorMessage.includes('NotAllowedError') && (
                  <li>カメラアクセスが許可されていません。権限を確認してください。</li>
                )}
                {testResult === 'failed' && errorMessage.includes('NotFoundError') && (
                  <li>カメラデバイスが見つかりません。接続を確認してください。</li>
                )}
              </ul>
            </AlertDescription>
          </Alert>
        )}
      </div>
    </div>
  )
}