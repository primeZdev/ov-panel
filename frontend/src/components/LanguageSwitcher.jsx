import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const languages = [
    {
      code: 'en',
      name: 'English',
      flag: '🇺🇸',
    },
    {
      code: 'fa',
      name: 'فارسی',
      flag: '🇮🇷',
    },
    {
      code: 'vi',
      name: 'Tiếng Việt',
      flag: '🇻🇳',
    },
  ];

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode);
    localStorage.setItem('language', langCode);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="language-switcher" ref={dropdownRef}>
      <button
        className="language-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Change language"
      >
        <span className="flag">{currentLanguage.flag}</span>
        <span className="language-name">{currentLanguage.name}</span>
        <svg
          className={`arrow ${isOpen ? 'open' : ''}`}
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M2.5 4.5L6 8L9.5 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="language-dropdown">
          {languages.map((lang) => (
            <button
              key={lang.code}
              className={`language-option ${lang.code === i18n.language ? 'active' : ''}`}
              onClick={() => handleLanguageChange(lang.code)}
            >
              <span className="flag">{lang.flag}</span>
              <span className="language-name">{lang.name}</span>
              {lang.code === i18n.language && (
                <svg
                  className="check-icon"
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M13.3333 4L6 11.3333L2.66667 8"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}

      <style jsx>{`
        .language-switcher {
          position: relative;
        }

        .language-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: transparent;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 14px;
          color: #374151;
        }

        .language-button:hover {
          background: #f9fafb;
          border-color: #d1d5db;
        }

        .flag {
          font-size: 20px;
          line-height: 1;
        }

        .language-name {
          font-weight: 500;
        }

        .arrow {
          transition: transform 0.2s ease;
          color: #6b7280;
        }

        .arrow.open {
          transform: rotate(180deg);
        }

        .language-dropdown {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                      0 4px 6px -2px rgba(0, 0, 0, 0.05);
          min-width: 180px;
          overflow: hidden;
          z-index: 1000;
          animation: slideDown 0.2s ease;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .language-option {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
          padding: 12px 16px;
          background: transparent;
          border: none;
          cursor: pointer;
          transition: background 0.2s ease;
          font-size: 14px;
          color: #374151;
          text-align: left;
        }

        .language-option:hover {
          background: #f9fafb;
        }

        .language-option.active {
          background: #eff6ff;
          color: #2563eb;
        }

        .language-option .language-name {
          flex: 1;
        }

        .check-icon {
          color: #2563eb;
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          .language-button {
            color: #f9fafb;
            border-color: #374151;
          }

          .language-button:hover {
            background: #1f2937;
            border-color: #4b5563;
          }

          .language-dropdown {
            background: #1f2937;
            border-color: #374151;
          }

          .language-option {
            color: #f9fafb;
          }

          .language-option:hover {
            background: #111827;
          }

          .language-option.active {
            background: #1e3a8a;
            color: #93c5fd;
          }
        }
      `}</style>
    </div>
  );
};

export default LanguageSwitcher;
