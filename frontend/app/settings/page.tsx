'use client';

import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/components/providers/AuthProvider';
import { Settings, Globe, User, Bell, Shield, Info, LogOut, Save, X } from 'lucide-react';
import { doc, getDoc, updateDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import toast from 'react-hot-toast';

interface UserProfile {
  name: string;
  age: string;
  gender: string;
  height: string;
  weight: string;
  goal: string;
  experience: string;
}

interface NotificationSettings {
  workoutReminder: boolean;
  mealReminder: boolean;
  progressUpdate: boolean;
  pushNotifications: boolean;
  emailNotifications: boolean;
}

export default function SettingsPage() {
  const { t, currentLanguage, changeLanguage, availableLanguages } = useLanguage();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: '',
    age: '',
    gender: '',
    height: '',
    weight: '',
    goal: '',
    experience: ''
  });
  const [notifications, setNotifications] = useState<NotificationSettings>({
    workoutReminder: true,
    mealReminder: true,
    progressUpdate: false,
    pushNotifications: true,
    emailNotifications: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load user profile
  useEffect(() => {
    const loadUserProfile = async () => {
      if (!user) return;
      
      setIsLoading(true);
      try {
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        if (userDoc.exists()) {
          const data = userDoc.data();
          setUserProfile({
            name: data.name || '',
            age: data.age || '',
            gender: data.gender || '',
            height: data.height || '',
            weight: data.weight || '',
            goal: data.goal || '',
            experience: data.experience || ''
          });
          
          if (data.notifications) {
            setNotifications(data.notifications);
          }
        }
      } catch (error) {
        console.error('Error loading profile:', error);
        toast.error(t('common.error'));
      } finally {
        setIsLoading(false);
      }
    };

    loadUserProfile();
  }, [user, t]);

  // Save settings
  const saveSettings = async () => {
    if (!user) return;
    
    setIsSaving(true);
    try {
      await updateDoc(doc(db, 'users', user.uid), {
        ...userProfile,
        notifications,
        language: currentLanguage,
        updatedAt: serverTimestamp()
      });
      
      toast.success(t('common.success'));
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error(t('common.error'));
    } finally {
      setIsSaving(false);
    }
  };

  const tabs = [
    { id: 'profile', label: t('settings.profile'), icon: User },
    { id: 'language', label: t('settings.language'), icon: Globe },
    { id: 'notifications', label: t('settings.notifications'), icon: Bell },
    { id: 'privacy', label: t('settings.privacy'), icon: Shield },
    { id: 'about', label: t('settings.about'), icon: Info }
  ];

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{t('common.error')}</p>
          <button
            onClick={() => window.location.href = '/auth/login'}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center">
              <Settings className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">{t('settings.title')}</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="flex flex-col md:flex-row">
            {/* Sidebar */}
            <div className="w-full md:w-1/4 border-b md:border-b-0 md:border-r border-gray-200">
              <nav className="p-4 space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {tab.label}
                    </button>
                  );
                })}
                
                {/* Logout button */}
                <button
                  onClick={logout}
                  className="w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors text-red-600 hover:bg-red-50 mt-4"
                >
                  <LogOut className="h-5 w-5 mr-3" />
                  {t('settings.logout')}
                </button>
              </nav>
            </div>

            {/* Main content */}
            <div className="flex-1 p-6">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
                </div>
              ) : (
                <>
                  {activeTab === 'profile' && (
                    <div className="space-y-6">
                      <h2 className="text-xl font-semibold">{t('settings.profile')}</h2>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.name')}
                          </label>
                          <input
                            type="text"
                            value={userProfile.name}
                            onChange={(e) => setUserProfile({...userProfile, name: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.age')}
                          </label>
                          <input
                            type="number"
                            value={userProfile.age}
                            onChange={(e) => setUserProfile({...userProfile, age: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.gender')}
                          </label>
                          <select
                            value={userProfile.gender}
                            onChange={(e) => setUserProfile({...userProfile, gender: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">{t('common.select')}</option>
                            <option value="male">{t('profile.male')}</option>
                            <option value="female">{t('profile.female')}</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.height')} (cm)
                          </label>
                          <input
                            type="number"
                            value={userProfile.height}
                            onChange={(e) => setUserProfile({...userProfile, height: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.weight')} (kg)
                          </label>
                          <input
                            type="number"
                            value={userProfile.weight}
                            onChange={(e) => setUserProfile({...userProfile, weight: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.goal')}
                          </label>
                          <select
                            value={userProfile.goal}
                            onChange={(e) => setUserProfile({...userProfile, goal: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">{t('common.select')}</option>
                            <option value="cutting">{t('profile.cutting')}</option>
                            <option value="bulking">{t('profile.bulking')}</option>
                            <option value="maintenance">{t('profile.maintenance')}</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            {t('profile.experience')}
                          </label>
                          <select
                            value={userProfile.experience}
                            onChange={(e) => setUserProfile({...userProfile, experience: e.target.value})}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">{t('common.select')}</option>
                            <option value="beginner">{t('profile.beginner')}</option>
                            <option value="intermediate">{t('profile.intermediate')}</option>
                            <option value="advanced">{t('profile.advanced')}</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === 'language' && (
                    <div className="space-y-6">
                      <h2 className="text-xl font-semibold">{t('settings.language')}</h2>
                      
                      <div className="space-y-4">
                        {Object.entries(availableLanguages).map(([code, lang]) => (
                          <button
                            key={code}
                            onClick={() => changeLanguage(code as any)}
                            className={`w-full flex items-center justify-between p-4 border rounded-lg transition-colors ${
                              currentLanguage === code
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-300 hover:bg-gray-50'
                            }`}
                          >
                            <div className="flex items-center">
                              <span className="text-2xl mr-3">{lang.flag}</span>
                              <span className="font-medium">{lang.name}</span>
                            </div>
                            {currentLanguage === code && (
                              <span className="text-blue-600">✓</span>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === 'notifications' && (
                    <div className="space-y-6">
                      <h2 className="text-xl font-semibold">{t('settings.notifications')}</h2>
                      
                      <div className="space-y-4">
                        {Object.entries(notifications).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
                            <span className="font-medium">{t(`notifications.${key}`)}</span>
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) => setNotifications({
                                  ...notifications,
                                  [key]: e.target.checked
                                } as NotificationSettings)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === 'privacy' && (
                    <div className="space-y-6">
                      <h2 className="text-xl font-semibold">{t('settings.privacy')}</h2>
                      <div className="space-y-4">
                        <p className="text-gray-600">
                          {currentLanguage === 'en' 
                            ? 'Your privacy and data security are important to us. We only collect necessary information for app functionality.'
                            : 'あなたのプライバシーとデータセキュリティは重要です。アプリの機能に必要な情報のみを収集します。'
                          }
                        </p>
                      </div>
                    </div>
                  )}

                  {activeTab === 'about' && (
                    <div className="space-y-6">
                      <h2 className="text-xl font-semibold">{t('settings.about')}</h2>
                      <div className="space-y-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h3 className="font-medium mb-2">TENAX FIT v3.0</h3>
                          <p className="text-gray-600">
                            {currentLanguage === 'en'
                              ? 'Enhanced AI-powered fitness platform with scientific analysis and personalized training programs.'
                              : 'AI技術を活用した科学的分析と個人最適化されたトレーニングプログラムを提供するフィットネスプラットフォーム。'
                            }
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Save button */}
                  {(activeTab === 'profile' || activeTab === 'notifications') && (
                    <div className="mt-8 flex justify-end space-x-4">
                      <button
                        onClick={saveSettings}
                        disabled={isSaving}
                        className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isSaving ? (
                          <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                        ) : (
                          <Save className="w-4 h-4 mr-2" />
                        )}
                        {t('settings.save')}
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}