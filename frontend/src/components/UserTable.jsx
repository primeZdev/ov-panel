import { useTranslation } from 'react-i18next';
import { FiCopy } from 'react-icons/fi';
import ActionsDropdown from './ActionsDropdown';
import './UserTable.css';

const UserTable = ({ users, onDelete, onDownload, onEdit, onToggleStatus, getSubscriptionLink }) => {
  const { t } = useTranslation();

  const handleCopyLink = (user) => {
    if (!getSubscriptionLink) return;
    const link = getSubscriptionLink(user);
    if (link) {
      navigator.clipboard.writeText(link);
      window.alert(t('copied_subscription_link', 'Subscription link copied!'));
    }
  };

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>{t('th_username')}</th>
            <th>{t('th_expiryDate')}</th>
            <th>{t('th_status')}</th>
            <th>{t('th_owner')}</th>
            <th>{t('th_actions')}</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr><td colSpan="5" style={{ textAlign: 'center' }}>No users found.</td></tr>
          ) : (
            users.map((user) => (
              <tr key={user.name}>
                <td>{user.name}</td>
                <td>{new Date(user.expiry_date).toLocaleDateString('en-CA')}</td>
                <td>
                  <span className={`status-${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? t('status_active') : t('status_inactive')}
                  </span>
                </td>
                <td>{user.owner}</td>
                <td style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ActionsDropdown
                    actions={[
                      { label: t('editButton'), onClick: () => onEdit(user) },
                      { label: t('downloadButton'), onClick: () => onDownload(user) },
                      {
                        label: user.is_active ? t('deactivateButton', 'Deactivate') : t('activateButton', 'Activate'),
                        onClick: () => onToggleStatus(user),
                        className: user.is_active ? 'warning-action' : 'success-action',
                      },
                      {
                        label: t('deleteButton'),
                        onClick: () => onDelete(user.name),
                        className: 'danger-action',
                      },
                    ]}
                  />
                  <button
                    className="icon-btn btn-copy"
                    title={t('copySubscriptionLink', 'Copy Link')}
                    onClick={() => handleCopyLink(user)}
                    style={{ background: 'none', border: 'none', padding: 0, marginLeft: 6, cursor: 'pointer' }}
                  >
                    <FiCopy style={{ fontSize: 20, color: '#90caf9' }} />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;