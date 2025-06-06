'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { UserCalibration } from '@/lib/mediapipe/types'
import toast from 'react-hot-toast'

interface CalibrationModalProps {
  open: boolean
  onClose: () => void
}

export function CalibrationModal({ open, onClose }: CalibrationModalProps) {
  const [calibration, setCalibration] = useState<UserCalibration>({
    height: 170,
    weight: 70,
    ankleMobility: 25,
  })

  const handleSave = () => {
    // LocalStorageに保存
    localStorage.setItem('userCalibration', JSON.stringify(calibration))
    toast.success('キャリブレーションを保存しました')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>個人キャリブレーション</DialogTitle>
          <DialogDescription>
            あなたの身体的特徴を入力してください。より正確なフォーム分析が可能になります。
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="space-y-2">
            <Label htmlFor="height">身長 (cm)</Label>
            <Input
              id="height"
              type="number"
              value={calibration.height}
              onChange={(e) =>
                setCalibration({ ...calibration, height: parseInt(e.target.value) || 0 })
              }
              min={100}
              max={250}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="weight">体重 (kg) - 任意</Label>
            <Input
              id="weight"
              type="number"
              value={calibration.weight || ''}
              onChange={(e) =>
                setCalibration({ ...calibration, weight: parseInt(e.target.value) || undefined })
              }
              min={30}
              max={200}
            />
          </div>

          <div className="space-y-2">
            <Label>足首の柔軟性 (度)</Label>
            <div className="flex items-center gap-4">
              <Slider
                value={[calibration.ankleMobility || 25]}
                onValueChange={(value) =>
                  setCalibration({ ...calibration, ankleMobility: value[0] })
                }
                min={10}
                max={45}
                step={5}
                className="flex-1"
              />
              <span className="w-12 text-right font-mono">
                {calibration.ankleMobility}°
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              壁に向かって膝を前に出せる最大角度
            </p>
          </div>

          <div className="space-y-4 pt-4 border-t">
            <h4 className="font-semibold">高度な設定（自動測定予定）</h4>
            <div className="space-y-2 opacity-50">
              <div className="flex justify-between">
                <span className="text-sm">大腿骨比率</span>
                <span className="text-sm">自動測定予定</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">脛骨比率</span>
                <span className="text-sm">自動測定予定</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">腕の長さ</span>
                <span className="text-sm">自動測定予定</span>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            キャンセル
          </Button>
          <Button onClick={handleSave}>保存</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}