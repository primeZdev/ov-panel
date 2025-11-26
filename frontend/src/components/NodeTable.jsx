import { useTranslation } from 'react-i18next';
import ActionsDropdown from './ActionsDropdown';

function getUsageColor(value) {
  if (value === undefined || value === null) return '';
  if (value <= 50) return 'usage-green';
  if (value <= 80) return 'usage-yellow';
  return 'usage-red';
}

const NodeTable = ({ nodes, isLoading, nodeInfo = {}, onDelete, onCheckStatus, onEdit }) => {
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
            <th>{t('cpuUsage', 'CPU')}</th>
            <th>{t('memoryUsage', 'RAM')}</th>
            <th>{t('th_actions')}</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan="7" style={{ textAlign: 'center' }}>Loading...</td>
            </tr>
          ) : nodes.length === 0 ? (
            <tr>
              <td colSpan="7" style={{ textAlign: 'center' }}>{t('noNodesFound')}</td>
            </tr>
          ) : (
            nodes.map((node) => {
              const info = nodeInfo[node.id] || {};
              return (
                <tr key={node.address}>
                  <td>{node.name}</td>
                  <td>{node.address}</td>
                  <td>{node.protocol}</td>
                  <td>
                    <span className={`status-${node.status ? 'active' : 'inactive'}`}>
                      {node.status ? t('status_active') : t('status_inactive')}
                    </span>
                  </td>
                  <td>
                    {info.cpu_usage !== undefined ? (
                      <span className={getUsageColor(info.cpu_usage)}>{info.cpu_usage + '%'}</span>
                    ) : '-'}
                  </td>
                  <td>
                    {info.memory_usage !== undefined ? (
                      <span className={getUsageColor(info.memory_usage)}>{info.memory_usage + '%'}</span>
                    ) : '-'}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <ActionsDropdown
                      actions={[
                        { label: t('editButton'), onClick: () => onEdit(node) },
                        { label: t('checkStatus'), onClick: () => onCheckStatus(node.id) },
                        {
                          label: t('deleteButton'),
                          onClick: () => onDelete(node.address, node.name),
                          className: 'danger-action',
                        },
                      ]}
                    />
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};

export default NodeTable;