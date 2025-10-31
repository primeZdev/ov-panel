import { NavLink } from 'react-router-dom';
import { FiGrid, FiUsers, FiServer, FiSettings } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import logoSrc from '../assets/Logo-Landscape-Dark.webp'; 

const Sidebar = () => {
  const { t } = useTranslation();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        {/* اصلاح: تگ img مستقیماً با کلاس جدید استایل‌دهی می‌شود */}
        <img 
          src={logoSrc} 
          alt="Panel Logo" 
          className="sidebar-logo" // کلاس جدید برای استایل‌دهی
        />
      </div>
      <nav>
        <ul>
          <li>
            <NavLink to="/" end className="nav-link">
              <div className="icon-wrapper">
                <FiGrid size={22} />
              </div>
              <span>{t('dashboard')}</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/users" className="nav-link">
              <div className="icon-wrapper">
                <FiUsers size={22} />
              </div>
              <span>{t('userManagement')}</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/nodes" className="nav-link">
              <div className="icon-wrapper">
                <FiServer size={22} />
              </div>
              <span>{t('nodeManagement')}</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/settings" className="nav-link">
              <div className="icon-wrapper">
                <FiSettings size={22} />
              </div>
              <span>{t('settings', 'Settings')}</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;