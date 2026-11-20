import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslation from './lang/en.json';
import faTranslation from './lang/fa.json';

const resources = {
  en: {
    translation: enTranslation,
  },
  fa: {
    translation: faTranslation,
  },
};

const savedLanguage = localStorage.getItem('language');
const initialLanguage = savedLanguage === 'fa' || savedLanguage === 'en'
  ? savedLanguage
  : 'en';

const applyDocumentLanguage = (language) => {
  const normalizedLanguage = language === 'fa' ? 'fa' : 'en';
  document.documentElement.lang = normalizedLanguage;
  document.documentElement.dir = normalizedLanguage === 'fa' ? 'rtl' : 'ltr';
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: initialLanguage,
    fallbackLng: 'en',

    interpolation: {
      escapeValue: false,
    },
  });

i18n.on('languageChanged', (language) => {
  const normalizedLanguage = language === 'fa' ? 'fa' : 'en';
  localStorage.setItem('language', normalizedLanguage);
  applyDocumentLanguage(normalizedLanguage);
});

applyDocumentLanguage(initialLanguage);

export default i18n;