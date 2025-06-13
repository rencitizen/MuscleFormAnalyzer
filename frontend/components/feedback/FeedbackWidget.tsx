'use client'

import { useState, useRef, useCallback } from 'react'
import { MessageSquare, X, Send, Camera, Bug, Lightbulb, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import toast from 'react-hot-toast'
// import html2canvas from 'html2canvas' // TODO: install this package

interface FeedbackData {
  type: 'bug' | 'feature' | 'usability' | 'other'
  severity: 'low' | 'medium' | 'high'
  description: string
  screenshot?: string
  userAgent: string
  timestamp: Date
  userId?: string
  pageUrl: string
  sessionId: string
}

const feedbackTypes = [
  { value: 'bug', label: 'バグ報告', icon: Bug },
  { value: 'feature', label: '機能要望', icon: Lightbulb },
  { value: 'usability', label: '使いやすさ', icon: MessageSquare },
  { value: 'other', label: 'その他', icon: AlertCircle }
]

export function FeedbackWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [type, setType] = useState<FeedbackData['type']>('usability')
  const [severity, setSeverity] = useState<FeedbackData['severity']>('medium')
  const [description, setDescription] = useState('')
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isTakingScreenshot, setIsTakingScreenshot] = useState(false)
  
  const widgetRef = useRef<HTMLDivElement>(null)

  // スクリーンショット撮影
  const captureScreenshot = useCallback(async () => {
    setIsTakingScreenshot(true)
    setIsOpen(false) // ダイアログを一時的に閉じる

    try {
      // TODO: html2canvasをインストール後に実装
      // 今はプレースホルダーとして動作
      toast.info('スクリーンショット機能はまもなく利用可能になります')
    } catch (error) {
      console.error('Screenshot capture failed:', error)
      toast.error('スクリーンショットの撮影に失敗しました')
    } finally {
      setIsTakingScreenshot(false)
      setIsOpen(true) // ダイアログを再度開く
    }
  }, [])

  // フィードバック送信
  const submitFeedback = async () => {
    if (!description.trim()) {
      toast.error('フィードバックを入力してください')
      return
    }

    setIsSubmitting(true)

    const feedbackData: FeedbackData = {
      type,
      severity,
      description: description.trim(),
      screenshot: screenshot || undefined,
      userAgent: navigator.userAgent,
      timestamp: new Date(),
      pageUrl: window.location.href,
      sessionId: sessionStorage.getItem('sessionId') || Date.now().toString()
    }

    try {
      // TODO: 実際のAPI実装
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      })

      if (response.ok) {
        toast.success('フィードバックを送信しました')
        
        // フォームをリセット
        setDescription('')
        setScreenshot(null)
        setType('usability')
        setSeverity('medium')
        setIsOpen(false)
      } else {
        throw new Error('Failed to submit feedback')
      }
    } catch (error) {
      console.error('Feedback submission failed:', error)
      
      // オフライン時はローカルストレージに保存
      const offlineFeedback = JSON.parse(localStorage.getItem('offlineFeedback') || '[]')
      offlineFeedback.push(feedbackData)
      localStorage.setItem('offlineFeedback', JSON.stringify(offlineFeedback))
      
      toast.success('オフラインで保存しました。オンライン時に自動送信されます')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      {/* フローティングボタン */}
      <div
        ref={widgetRef}
        data-feedback-widget
        className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
          isMinimized ? 'opacity-50 hover:opacity-100' : ''
        }`}
      >
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
          title="フィードバックを送る"
        >
          <MessageSquare className="h-5 w-5 mr-2" />
          フィードバック
        </Button>
      </div>

      {/* フィードバックダイアログ */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>フィードバックを送る</DialogTitle>
            <DialogDescription>
              アプリの改善にご協力ください。すべてのフィードバックは匿名で送信されます。
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            {/* フィードバックタイプ */}
            <div className="space-y-2">
              <Label>フィードバックの種類</Label>
              <RadioGroup value={type} onValueChange={(value) => setType(value as FeedbackData['type'])}>
                <div className="grid grid-cols-2 gap-2">
                  {feedbackTypes.map(({ value, label, icon: Icon }) => (
                    <div key={value} className="flex items-center space-x-2">
                      <RadioGroupItem value={value} id={value} />
                      <Label
                        htmlFor={value}
                        className="flex items-center gap-2 cursor-pointer"
                      >
                        <Icon className="h-4 w-4" />
                        {label}
                      </Label>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>

            {/* 重要度（バグの場合のみ） */}
            {type === 'bug' && (
              <div className="space-y-2">
                <Label>重要度</Label>
                <RadioGroup value={severity} onValueChange={(value) => setSeverity(value as FeedbackData['severity'])}>
                  <div className="flex gap-4">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="low" id="low" />
                      <Label htmlFor="low">低</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="medium" id="medium" />
                      <Label htmlFor="medium">中</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="high" id="high" />
                      <Label htmlFor="high">高</Label>
                    </div>
                  </div>
                </RadioGroup>
              </div>
            )}

            {/* 詳細説明 */}
            <div className="space-y-2">
              <Label htmlFor="description">詳細説明</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={
                  type === 'bug' 
                    ? 'どのような問題が発生しましたか？再現手順も教えてください。'
                    : type === 'feature'
                    ? 'どのような機能があると便利ですか？'
                    : '使いにくい点や改善してほしい点を教えてください。'
                }
                rows={4}
                className="resize-none"
              />
            </div>

            {/* スクリーンショット */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>スクリーンショット（任意）</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={captureScreenshot}
                  disabled={isTakingScreenshot}
                >
                  <Camera className="h-4 w-4 mr-2" />
                  {isTakingScreenshot ? '撮影中...' : '画面を撮影'}
                </Button>
              </div>
              
              {screenshot && (
                <div className="relative">
                  <img
                    src={screenshot}
                    alt="Screenshot"
                    className="w-full h-32 object-cover rounded-md border"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute top-1 right-1"
                    onClick={() => setScreenshot(null)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* 送信ボタン */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsOpen(false)}
                disabled={isSubmitting}
              >
                キャンセル
              </Button>
              <Button
                onClick={submitFeedback}
                disabled={isSubmitting || !description.trim()}
              >
                <Send className="h-4 w-4 mr-2" />
                {isSubmitting ? '送信中...' : '送信'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}