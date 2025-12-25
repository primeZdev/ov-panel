import { NavLink } from 'react-router-dom';
import { FiGrid, FiUsers, FiServer } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import logoSrc from '../assets/Logo-Landscape-Dark.webp';

const Sidebar = () => {
  const { t } = useTranslation();
  const { userRole } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <img
          src={logoSrc}
          alt="Panel Logo"
          className="sidebar-logo"
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
          {userRole !== 'admin' && (
            <li>
              <NavLink to="/nodes" className="nav-link">
                <div className="icon-wrapper">
                  <FiServer size={22} />
                </div>
                <span>{t('nodeManagement')}</span>
              </NavLink>
            </li>
          )}
          {userRole === 'main_admin' && (
            <li>
              <NavLink to="/admins" className="nav-link">
                <div className="icon-wrapper">
                  <FiUsers size={22} />
                </div>
                <span>{t('adminManagement')}</span>
              </NavLink>
            </li>
          )}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;