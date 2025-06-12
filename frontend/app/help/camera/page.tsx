'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Camera, Smartphone, Globe, Shield, AlertCircle, CheckCircle } from 'lucide-react'
import Image from 'next/image'

export default function CameraHelpPage() {
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">カメラ機能のヘルプ</h1>
      
      <div className="space-y-6">
        {/* 概要 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="w-5 h-5" />
              カメラ機能について
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>
              MuscleFormAnalyzerでは、食事の撮影とフォーム分析でカメラを使用します。
              モバイルデバイスやPCのカメラを使って、リアルタイムで撮影・分析が可能です。
            </p>
          </CardContent>
        </Card>

        {/* 要件 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              必要な要件
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold">HTTPS接続</h3>
                  <p className="text-sm text-gray-600">
                    セキュリティのため、HTTPSでの接続が必要です。
                    http://で始まるURLではカメラが使用できません。
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold">対応ブラウザ</h3>
                  <ul className="text-sm text-gray-600 mt-1 space-y-1">
                    <li>• Chrome/Edge 74以上</li>
                    <li>• Safari 12以上</li>
                    <li>• Firefox 60以上</li>
                  </ul>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold">カメラ権限</h3>
                  <p className="text-sm text-gray-600">
                    ブラウザからカメラへのアクセス許可が必要です。
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 権限の許可方法 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="w-5 h-5" />
              カメラ権限の許可方法
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Chrome/Edge */}
            <div>
              <h3 className="font-semibold mb-2">Chrome/Edgeの場合</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>カメラボタンをクリック時に権限要求が表示されます</li>
                <li>「許可」をクリックしてください</li>
                <li>アドレスバー左側のカメラアイコンから設定変更も可能です</li>
              </ol>
            </div>

            {/* Safari */}
            <div>
              <h3 className="font-semibold mb-2">Safari（iOS）の場合</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>設定アプリを開く</li>
                <li>Safari → カメラ</li>
                <li>「確認」または「許可」を選択</li>
              </ol>
            </div>

            {/* Android */}
            <div>
              <h3 className="font-semibold mb-2">Android Chromeの場合</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>サイト設定（URLバー左の鍵アイコン）をタップ</li>
                <li>「権限」→「カメラ」</li>
                <li>「許可」を選択</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        {/* トラブルシューティング */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              トラブルシューティング
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>カメラが起動しない場合</AlertTitle>
              <AlertDescription className="mt-2 space-y-2">
                <p>1. HTTPS接続か確認（URLがhttps://で始まっているか）</p>
                <p>2. 他のアプリでカメラを使用していないか確認</p>
                <p>3. ブラウザを再起動してみる</p>
                <p>4. デバイスを再起動してみる</p>
              </AlertDescription>
            </Alert>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>権限エラーが出る場合</AlertTitle>
              <AlertDescription className="mt-2 space-y-2">
                <p>1. ブラウザの設定でサイトの権限をリセット</p>
                <p>2. プライベートブラウジングモードでは制限される場合があります</p>
                <p>3. デバイスの設定でカメラがブロックされていないか確認</p>
              </AlertDescription>
            </Alert>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>画質が悪い場合</AlertTitle>
              <AlertDescription className="mt-2 space-y-2">
                <p>1. 十分な明るさがある場所で撮影</p>
                <p>2. カメラレンズが汚れていないか確認</p>
                <p>3. 安定したネットワーク接続を確保</p>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* 代替手段 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              カメラが使えない場合の代替手段
            </CardTitle>
            <CardDescription>
              カメラ機能が利用できない場合でも、以下の方法で利用可能です
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold mb-2">ファイルアップロード</h3>
                <p className="text-sm">
                  事前に撮影した写真をアップロードすることで、同様の分析が可能です。
                  「ファイル選択」ボタンから画像を選択してください。
                </p>
              </div>

              <div className="p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold mb-2">モバイルアプリでの撮影</h3>
                <p className="text-sm">
                  スマートフォンの標準カメラアプリで撮影し、
                  その画像をアップロードすることも可能です。
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* プライバシー */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              プライバシーとセキュリティ
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm">
              • カメラへのアクセスはブラウザ内でのみ行われます
            </p>
            <p className="text-sm">
              • 撮影した画像は分析のためにのみ使用されます
            </p>
            <p className="text-sm">
              • カメラ権限はいつでも取り消すことができます
            </p>
            <p className="text-sm">
              • HTTPSによる暗号化通信で保護されています
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}