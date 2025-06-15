export const LANGUAGES = {
  ja: {
    code: 'ja',
    name: '日本語',
    flag: '🇯🇵'
  },
  en: {
    code: 'en', 
    name: 'English',
    flag: '🇺🇸'
  }
} as const;

export type LanguageCode = keyof typeof LANGUAGES;