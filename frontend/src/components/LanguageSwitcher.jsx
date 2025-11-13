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
          background: var(--background-primary);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 14px;
          color: var(--text-primary);
          width: 100%;
        }

        .language-button:hover {
          background: var(--background-card-hover);
          border-color: var(--accent-color);
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
          color: var(--text-secondary);
          margin-left: auto;
        }

        .arrow.open {
          transform: rotate(180deg);
        }

        .language-dropdown {
          position: absolute;
          bottom: calc(100% + 8px);
          left: 0;
          right: 0;
          background: var(--background-card-hover);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          box-shadow: 0 -10px 25px -3px rgba(0, 0, 0, 0.5),
                      0 -4px 6px -2px rgba(0, 0, 0, 0.3);
          overflow: hidden;
          z-index: 1000;
          animation: slideUp 0.2s ease;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(10px);
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
          color: var(--text-primary);
          text-align: left;
        }

        .language-option:hover {
          background: var(--background-secondary);
        }

        .language-option.active {
          background: var(--accent-color-transparent);
          color: var(--accent-color);
        }

        .language-option .language-name {
          flex: 1;
        }

        .check-icon {
          color: var(--accent-color);
        }
      `}</style>
        </div>
    );
};

export default LanguageSwitcher;
