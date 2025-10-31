import { NavLink } from 'react-router-dom';
import { FiGrid, FiUsers, FiServer, FiSettings } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const MobileNav = () => {
  const { t } = useTranslation();

  return (
    <nav className="mobile-nav">
      <NavLink to="/" end className="mobile-nav-link">
        <FiGrid size={22} />
        <span>{t('dashboard')}</span>
      </NavLink>
      <NavLink to="/users" className="mobile-nav-link">
        <FiUsers size={22} />
        <span>{t('users')}</span>
      </NavLink>
      <NavLink to="/nodes" className="mobile-nav-link">
        <FiServer size={22} />
        <span>{t('nodes')}</span>
      </NavLink>
      <NavLink to="/settings" className="mobile-nav-link">
        <FiSettings size={22} />
        <span>{t('settings')}</span>
      </NavLink>
    </nav>
  );
};

export default MobileNav;