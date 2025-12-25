import { NavLink } from 'react-router-dom';
import { FiGrid, FiUsers, FiServer } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

const MobileNav = () => {
  const { t } = useTranslation();
  const { userRole } = useAuth();

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
      {userRole !== 'admin' && (
        <NavLink to="/nodes" className="mobile-nav-link">
          <FiServer size={22} />
          <span>{t('nodes')}</span>
        </NavLink>
      )}
      {userRole === 'main_admin' && (
        <NavLink to="/admins" className="mobile-nav-link">
          <FiUsers size={22} />
          <span>{t('admins')}</span>
        </NavLink>
      )}
    </nav>
  );
};

export default MobileNav;