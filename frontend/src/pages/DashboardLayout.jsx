import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import MobileNav from '../components/MobileNav'; 
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { FiLogOut, FiRefreshCw, FiGithub, FiSend, FiGlobe } from 'react-icons/fi';
import logoSrc from '../assets/Logo-Landscape-Dark.webp'; 

const DashboardLayout = () => {
  const { logout } = useAuth();
  const { t, i18n } = useTranslation();

  const handleRefresh = () => {
    window.location.reload();
  };

  const changeLanguage = () => {
    const newLang = i18n.language === 'en' ? 'fa' : 'en';
    i18n.changeLanguage(newLang);
    document.documentElement.dir = newLang === 'fa' ? 'rtl' : 'ltr';
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
            <a href="https://t.me/OVPanel" target="_blank" rel="noopener noreferrer" className="action-btn">
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
    </div>
  );
};

export default DashboardLayout;