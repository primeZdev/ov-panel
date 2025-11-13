import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslation from './lang/en.json';
import faTranslation from './lang/fa.json';
import viTranslation from './lang/vi.json';

const resources = {
  en: {
    translation: enTranslation,
  },
  fa: {
    translation: faTranslation,
  },
  vi: {
    translation: viTranslation,
  },
};

// Get saved language from localStorage or default to 'en'
const savedLanguage = localStorage.getItem('language') || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage, 
    fallbackLng: 'en', 

    interpolation: {
      escapeValue: false, 
    },
  });

export default i18n;