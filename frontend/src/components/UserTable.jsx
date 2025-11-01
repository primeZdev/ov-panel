import { useTranslation } from 'react-i18next';
import ActionsDropdown from './ActionsDropdown'; 

const UserTable = ({ users, onDelete, onDownload, onEdit }) => {
  const { t } = useTranslation();

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
                <td style={{ textAlign: 'right' }}>
                  <ActionsDropdown
                    actions={[
                      { label: t('editButton'), onClick: () => onEdit(user) },
                      { label: t('downloadButton'), onClick: () => onDownload(user) },
                      {
                        label: t('deleteButton'),
                        onClick: () => onDelete(user.name),
                        className: 'danger-action',
                      },
                    ]}
                  />
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