'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  User,
  Settings,
  Target,
  Bell,
  Shield,
  Save,
  Camera,
  Check,
  AlertCircle
} from 'lucide-react'

interface UserProfile {
  name: string
  email: string
  bio: string
  age: string
  gender: 'male' | 'female' | 'other'
  height: string
  currentWeight: string
  targetWeight: string
  activityLevel: string
  fitnessGoal: string
  dietaryRestrictions: string
  medicalConditions: string
  preferredUnits: 'metric' | 'imperial'
  notifications: {
    email: boolean
    push: boolean
    reminders: boolean
  }
  privacy: {
    publicProfile: boolean
    shareProgress: boolean
    showStats: boolean
  }
}

export default function ProfilePage() {
  const { data: session } = useSession()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const [profile, setProfile] = useState<UserProfile>({
    name: session?.user?.name || '',
    email: session?.user?.email || '',
    bio: '筋トレとランニングが趣味です。健康的な体作りを目指しています。',
    age: '30',
    gender: 'male',
    height: '175',
    currentWeight: '73.2',
    targetWeight: '70',
    activityLevel: 'moderate',
    fitnessGoal: 'fat_loss',
    dietaryRestrictions: '',
    medicalConditions: '',
    preferredUnits: 'metric',
    notifications: {
      email: true,
      push: true,
      reminders: true
    },
    privacy: {
      publicProfile: false,
      shareProgress: true,
      showStats: true
    }
  })

  const activityLevels = [
    { value: 'sedentary', label: '座りがち' },
    { value: 'light', label: '軽い運動' },
    { value: 'moderate', label: '中程度' },
    { value: 'active', label: '活発' },
    { value: 'very_active', label: '非常に活発' }
  ]

  const fitnessGoals = [
    { value: 'fat_loss', label: '減量' },
    { value: 'muscle_gain', label: '筋肉増量' },
    { value: 'maintain', label: '現状維持' },
    { value: 'performance', label: 'パフォーマンス向上' },
    { value: 'health', label: '健康改善' }
  ]

  const handleSave = async () => {
    setIsSaving(true)
    // API呼び出しのシミュレーション
    setTimeout(() => {
      setIsSaving(false)
      setSaveSuccess(true)
      setIsEditing(false)
      setTimeout(() => setSaveSuccess(false), 3000)
    }, 1000)
  }

  const handleAvatarUpload = () => {
    // アバター画像アップロード処理
    console.log('Avatar upload')
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">プロファイル</h1>
        <p className="text-muted-foreground">あなたの情報と設定を管理</p>
      </div>

      {saveSuccess && (
        <Alert className="mb-4">
          <Check className="h-4 w-4" />
          <AlertDescription>
            プロファイルが正常に保存されました
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左側：プロフィール画像とクイック情報 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>プロフィール</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="relative inline-block mb-4">
                <Avatar className="w-32 h-32">
                  <AvatarImage src={session?.user?.image || ''} />
                  <AvatarFallback>
                    <User className="w-16 h-16" />
                  </AvatarFallback>
                </Avatar>
                <Button
                  size="sm"
                  variant="outline"
                  className="absolute bottom-0 right-0 rounded-full w-10 h-10 p-0"
                  onClick={handleAvatarUpload}
                >
                  <Camera className="w-4 h-4" />
                </Button>
              </div>
              <h3 className="text-xl font-semibold mb-2">{profile.name}</h3>
              <p className="text-sm text-muted-foreground mb-4">{profile.email}</p>
              <p className="text-sm mb-4">{profile.bio}</p>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">年齢:</span>
                  <span>{profile.age}歳</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">身長:</span>
                  <span>{profile.height}cm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">現在体重:</span>
                  <span>{profile.currentWeight}kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">目標体重:</span>
                  <span>{profile.targetWeight}kg</span>
                </div>
              </div>

              <Button
                className="w-full mt-6"
                onClick={() => setIsEditing(!isEditing)}
                variant={isEditing ? "outline" : "default"}
              >
                {isEditing ? 'キャンセル' : '編集する'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 右側：詳細設定 */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="basic" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basic">
                <User className="w-4 h-4 mr-2" />
                基本情報
              </TabsTrigger>
              <TabsTrigger value="fitness">
                <Target className="w-4 h-4 mr-2" />
                フィットネス
              </TabsTrigger>
              <TabsTrigger value="notifications">
                <Bell className="w-4 h-4 mr-2" />
                通知
              </TabsTrigger>
              <TabsTrigger value="privacy">
                <Shield className="w-4 h-4 mr-2" />
                プライバシー
              </TabsTrigger>
            </TabsList>

            <TabsContent value="basic">
              <Card>
                <CardHeader>
                  <CardTitle>基本情報</CardTitle>
                  <CardDescription>
                    あなたの基本的な情報を入力してください
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="name">名前</Label>
                      <Input
                        id="name"
                        value={profile.name}
                        onChange={(e) => setProfile({...profile, name: e.target.value})}
                        disabled={!isEditing}
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">メールアドレス</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profile.email}
                        disabled
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="bio">自己紹介</Label>
                    <Textarea
                      id="bio"
                      value={profile.bio}
                      onChange={(e) => setProfile({...profile, bio: e.target.value})}
                      disabled={!isEditing}
                      rows={3}
                    />
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="age">年齢</Label>
                      <Input
                        id="age"
                        type="number"
                        value={profile.age}
                        onChange={(e) => setProfile({...profile, age: e.target.value})}
                        disabled={!isEditing}
                      />
                    </div>
                    <div>
                      <Label>性別</Label>
                      <RadioGroup
                        value={profile.gender}
                        onValueChange={(value) => setProfile({...profile, gender: value as any})}
                        disabled={!isEditing}
                      >
                        <div className="flex space-x-4">
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="male" id="male" />
                            <Label htmlFor="male">男性</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="female" id="female" />
                            <Label htmlFor="female">女性</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <RadioGroupItem value="other" id="other" />
                            <Label htmlFor="other">その他</Label>
                          </div>
                        </div>
                      </RadioGroup>
                    </div>
                  </div>

                  <div>
                    <Label>単位設定</Label>
                    <RadioGroup
                      value={profile.preferredUnits}
                      onValueChange={(value) => setProfile({...profile, preferredUnits: value as any})}
                      disabled={!isEditing}
                    >
                      <div className="flex space-x-4">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="metric" id="metric" />
                          <Label htmlFor="metric">メートル法 (kg, cm)</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="imperial" id="imperial" />
                          <Label htmlFor="imperial">ヤード・ポンド法 (lb, inch)</Label>
                        </div>
                      </div>
                    </RadioGroup>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="fitness">
              <Card>
                <CardHeader>
                  <CardTitle>フィットネス情報</CardTitle>
                  <CardDescription>
                    あなたの健康とフィットネスに関する情報
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <Label htmlFor="height">身長 (cm)</Label>
                      <Input
                        id="height"
                        type="number"
                        value={profile.height}
                        onChange={(e) => setProfile({...profile, height: e.target.value})}
                        disabled={!isEditing}
                      />
                    </div>
                    <div>
                      <Label htmlFor="currentWeight">現在の体重 (kg)</Label>
                      <Input
                        id="currentWeight"
                        type="number"
                        step="0.1"
                        value={profile.currentWeight}
                        onChange={(e) => setProfile({...profile, currentWeight: e.target.value})}
                        disabled={!isEditing}
                      />
                    </div>
                    <div>
                      <Label htmlFor="targetWeight">目標体重 (kg)</Label>
                      <Input
                        id="targetWeight"
                        type="number"
                        step="0.1"
                        value={profile.targetWeight}
                        onChange={(e) => setProfile({...profile, targetWeight: e.target.value})}
                        disabled={!isEditing}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="activityLevel">活動レベル</Label>
                    <Select
                      value={profile.activityLevel}
                      onValueChange={(value) => setProfile({...profile, activityLevel: value})}
                      disabled={!isEditing}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {activityLevels.map((level) => (
                          <SelectItem key={level.value} value={level.value}>
                            {level.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="fitnessGoal">フィットネス目標</Label>
                    <Select
                      value={profile.fitnessGoal}
                      onValueChange={(value) => setProfile({...profile, fitnessGoal: value})}
                      disabled={!isEditing}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {fitnessGoals.map((goal) => (
                          <SelectItem key={goal.value} value={goal.value}>
                            {goal.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="dietaryRestrictions">食事制限・アレルギー</Label>
                    <Textarea
                      id="dietaryRestrictions"
                      placeholder="例：ベジタリアン、乳糖不耐症、ナッツアレルギー"
                      value={profile.dietaryRestrictions}
                      onChange={(e) => setProfile({...profile, dietaryRestrictions: e.target.value})}
                      disabled={!isEditing}
                      rows={2}
                    />
                  </div>

                  <div>
                    <Label htmlFor="medicalConditions">既往症・健康上の注意事項</Label>
                    <Textarea
                      id="medicalConditions"
                      placeholder="例：高血圧、糖尿病、腰痛"
                      value={profile.medicalConditions}
                      onChange={(e) => setProfile({...profile, medicalConditions: e.target.value})}
                      disabled={!isEditing}
                      rows={2}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="notifications">
              <Card>
                <CardHeader>
                  <CardTitle>通知設定</CardTitle>
                  <CardDescription>
                    通知の受け取り方法を設定します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="email-notifications">メール通知</Label>
                      <p className="text-sm text-muted-foreground">
                        重要な更新やお知らせをメールで受け取る
                      </p>
                    </div>
                    <Switch
                      id="email-notifications"
                      checked={profile.notifications.email}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          notifications: {...profile.notifications, email: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="push-notifications">プッシュ通知</Label>
                      <p className="text-sm text-muted-foreground">
                        アプリからのプッシュ通知を受け取る
                      </p>
                    </div>
                    <Switch
                      id="push-notifications"
                      checked={profile.notifications.push}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          notifications: {...profile.notifications, push: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="reminders">リマインダー</Label>
                      <p className="text-sm text-muted-foreground">
                        トレーニングや測定のリマインダーを受け取る
                      </p>
                    </div>
                    <Switch
                      id="reminders"
                      checked={profile.notifications.reminders}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          notifications: {...profile.notifications, reminders: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="privacy">
              <Card>
                <CardHeader>
                  <CardTitle>プライバシー設定</CardTitle>
                  <CardDescription>
                    データの共有と公開設定を管理します
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="public-profile">公開プロフィール</Label>
                      <p className="text-sm text-muted-foreground">
                        他のユーザーがあなたのプロフィールを閲覧できるようにする
                      </p>
                    </div>
                    <Switch
                      id="public-profile"
                      checked={profile.privacy.publicProfile}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          privacy: {...profile.privacy, publicProfile: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="share-progress">進捗の共有</Label>
                      <p className="text-sm text-muted-foreground">
                        フレンドと進捗を共有する
                      </p>
                    </div>
                    <Switch
                      id="share-progress"
                      checked={profile.privacy.shareProgress}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          privacy: {...profile.privacy, shareProgress: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="show-stats">統計情報の表示</Label>
                      <p className="text-sm text-muted-foreground">
                        プロフィールに統計情報を表示する
                      </p>
                    </div>
                    <Switch
                      id="show-stats"
                      checked={profile.privacy.showStats}
                      onCheckedChange={(checked) => 
                        setProfile({
                          ...profile, 
                          privacy: {...profile.privacy, showStats: checked}
                        })
                      }
                      disabled={!isEditing}
                    />
                  </div>

                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      あなたのデータは安全に保護されています。個人情報は第三者と共有されません。
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {isEditing && (
            <Button 
              className="w-full mt-4" 
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? (
                <>保存中...</>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  変更を保存
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}