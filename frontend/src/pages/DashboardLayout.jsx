import { Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import MobileNav from '../components/MobileNav'; 
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { FiLogOut, FiRefreshCw, FiGithub, FiSend, FiGlobe, FiAlertCircle, FiExternalLink } from 'react-icons/fi';
import apiClient from '../services/api';
import ReactMarkdown from 'react-markdown';
import logoSrc from '../assets/Logo-Landscape-Dark.webp'; 

const DashboardLayout = () => {
  const { logout } = useAuth();
  const { t, i18n } = useTranslation();
  const [updateInfo, setUpdateInfo] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);

  const handleRefresh = () => {
    window.location.reload();
  };

  const changeLanguage = () => {
    const newLang = i18n.language === 'en' ? 'fa' : 'en';
    i18n.changeLanguage(newLang);
    document.documentElement.dir = newLang === 'fa' ? 'rtl' : 'ltr';
  };

  const checkForUpdate = async () => {
    try {
      const response = await apiClient.get('/server/check-update');
      if (response.data.success && response.data.data.update_available) {
        setUpdateInfo(response.data.data);
        setShowUpdateModal(true);
      }
    } catch (error) {
      console.error('Failed to check for updates:', error);
    }
  };

  useEffect(() => {
    checkForUpdate();
  }, []);

  const handleUpdateClick = () => {
    window.open(updateInfo.release_url, '_blank', 'noopener,noreferrer');
    setShowUpdateModal(false);
  };

  const handleDismissUpdate = () => {
    setShowUpdateModal(false);
  };

  return (
    <div id="main-container">
      <Sidebar />
      <div className="content-wrapper">
        <header className="main-header">
          {/* Logo container, visible only on mobile */}
          <div className="header-logo-container">
            <img src={logoSrc} alt="Panel Logo" className="header-logo" />
          </div>
          <div className="header-actions">
            <a href="https://t.me/primezdev" target="_blank" rel="noopener noreferrer" className="action-btn">
              <FiSend size={18} />
            </a>
            <a href="https://github.com/primeZdev/ov-panel" target="_blank" rel="noopener noreferrer" className="action-btn">
              <FiGithub size={18} />
            </a>
            <button onClick={changeLanguage} className="action-btn">
              <FiGlobe size={18} />
            </button>
            <button onClick={handleRefresh} className="action-btn">
              <FiRefreshCw size={18} />
            </button>
            <button onClick={logout} className="btn btn-danger" style={{width: 'auto', display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px'}}>
              <FiLogOut />
              <span className="logout-text">{t('logout')}</span>
            </button>
          </div>
        </header>
        <main>
          <Outlet />
        </main>
      </div>
      <MobileNav />

      {showUpdateModal && updateInfo && (
        <div className="update-modal-overlay" onClick={handleDismissUpdate}>
          <div className="update-modal" onClick={(e) => e.stopPropagation()}>
            <div className="update-modal-header">
              <FiAlertCircle size={24} className="update-icon" />
              <h3>{t('updateAvailable') || 'Update Available'}</h3>
            </div>
            <div className="update-modal-body">
              <p>{t('currentVersion') || 'Current version'}: <strong>{updateInfo.current_version}</strong></p>
              <p>{t('latestVersion') || 'Latest version'}: <strong>{updateInfo.latest_version}</strong></p>
              {updateInfo.release_notes && (
                <div className="release-notes">
                  <h4>{t('releaseNotes') || 'Release Notes'}:</h4>
                  <ReactMarkdown className="release-notes-content">
                    {updateInfo.release_notes}
                  </ReactMarkdown>
                </div>
              )}
            </div>
            <div className="update-modal-footer">
              <button className="btn btn-secondary" onClick={handleDismissUpdate}>
                {t('dismiss') || 'Dismiss'}
              </button>
              <button className="btn btn-primary" onClick={handleUpdateClick}>
                <FiExternalLink size={16} /> {t('viewRelease') || 'View Release'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardLayout;