'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Language, TranslationKey } from '@/lib/i18n/translations';
import { LANGUAGES, LanguageCode } from '@/lib/i18n/languages';
import { doc, updateDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { useAuth } from '@/components/providers/AuthProvider';

interface LanguageContextType {
  currentLanguage: LanguageCode;
  changeLanguage: (langCode: LanguageCode) => Promise<void>;
  t: (key: string) => string;
  isLoading: boolean;
  availableLanguages: typeof LANGUAGES;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>('ja');
  const [isLoading, setIsLoading] = useState(true);
  const { user } = useAuth();

  // Load saved language setting
  useEffect(() => {
    const loadLanguage = async () => {
      try {
        const savedLanguage = localStorage.getItem('tenax_language') as LanguageCode;
        if (savedLanguage && LANGUAGES[savedLanguage]) {
          setCurrentLanguage(savedLanguage);
        } else {
          // Detect browser language
          const browserLang = navigator.language.split('-')[0] as LanguageCode;
          if (LANGUAGES[browserLang]) {
            setCurrentLanguage(browserLang);
          }
        }
      } catch (error) {
        console.error('Error loading language settings:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadLanguage();
  }, []);

  // Load user's language preference from Firebase when logged in
  useEffect(() => {
    const loadUserLanguage = async () => {
      if (user) {
        try {
          const { doc, getDoc } = await import('firebase/firestore');
          const userDoc = await getDoc(doc(db, 'users', user.uid));
          
          if (userDoc.exists()) {
            const userData = userDoc.data();
            if (userData.language && LANGUAGES[userData.language as LanguageCode]) {
              setCurrentLanguage(userData.language as LanguageCode);
              localStorage.setItem('tenax_language', userData.language);
              document.documentElement.lang = userData.language;
            }
          }
        } catch (error) {
          console.error('Error loading user language from Firebase:', error);
        }
      }
    };

    loadUserLanguage();
  }, [user]);

  // Change language
  const changeLanguage = async (langCode: LanguageCode) => {
    try {
      if (LANGUAGES[langCode]) {
        setCurrentLanguage(langCode);
        localStorage.setItem('tenax_language', langCode);
        
        // Update HTML lang attribute
        document.documentElement.lang = langCode;
        
        // Save to Firestore if user is logged in
        if (user) {
          await updateUserLanguage(user.uid, langCode);
        }
      }
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  // Translation function
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[currentLanguage];
    
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k];
      } else {
        // Fallback to Japanese
        value = translations.ja;
        for (const fallbackKey of keys) {
          if (value && typeof value === 'object') {
            value = value[fallbackKey];
          } else {
            return key; // Return key if translation not found
          }
        }
        break;
      }
    }
    
    return value || key;
  };

  const value: LanguageContextType = {
    currentLanguage,
    changeLanguage,
    t,
    isLoading,
    availableLanguages: LANGUAGES
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

// Update user language in Firestore
const updateUserLanguage = async (userId: string, language: LanguageCode) => {
  try {
    const userRef = doc(db, 'users', userId);
    await updateDoc(userRef, {
      language,
      updatedAt: serverTimestamp()
    });
  } catch (error) {
    console.error('Error saving language settings:', error);
  }
};