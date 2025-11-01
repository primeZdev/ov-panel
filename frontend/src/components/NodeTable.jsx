import { useTranslation } from 'react-i18next';
import ActionsDropdown from './ActionsDropdown'; // Import the new component

const NodeTable = ({ nodes, isLoading, onDelete, onCheckStatus, onEdit }) => {
  const { t } = useTranslation();

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>{t('th_nodeName')}</th>
            <th>{t('th_address')}</th>
            <th>{t('th_protocol')}</th>
            <th>{t('th_status')}</th>
            <th>{t('th_actions')}</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan="5" style={{ textAlign: 'center' }}>Loading...</td>
            </tr>
          ) : nodes.length === 0 ? (
            <tr>
              <td colSpan="5" style={{ textAlign: 'center' }}>{t('noNodesFound')}</td>
            </tr>
          ) : (
            nodes.map((node) => (
              <tr key={node.address}>
                <td>{node.name}</td>
                <td>{node.address}</td>
                <td>{node.protocol}</td>
                <td>
                  <span className={`status-${node.status ? 'active' : 'inactive'}`}>
                    {node.status ? t('status_active') : t('status_inactive')}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <ActionsDropdown
                    actions={[
                      { label: t('editButton'), onClick: () => onEdit(node) },
                      { label: t('checkStatus'), onClick: () => onCheckStatus(node.address) },
                      {
                        label: t('deleteButton'),
                        onClick: () => onDelete(node.address, node.name),
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

export default NodeTable;