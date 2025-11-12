import { useTranslation } from 'react-i18next';
import ActionsDropdown from './ActionsDropdown';
import { FiCircle } from 'react-icons/fi';

const NodeTable = ({ nodes, isLoading, onDelete, onCheckStatus, onEdit }) => {
  const { t } = useTranslation();

  const getStatusIcon = (status) => {
    return status === 'online' ? (
      <FiCircle className="status-icon online" />
    ) : (
      <FiCircle className="status-icon offline" />
    );
  };

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>{t('th_nodeName')}</th>
            <th>{t('th_address')}</th>
            <th>{t('th_protocol')}</th>
            <th>{t('th_status')}</th>
            <th>{t('th_cpuUsage')}</th>
            <th>{t('th_memoryUsage')}</th>
            <th>{t('th_responseTime')}</th>
            <th>{t('th_actions')}</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan="8" style={{ textAlign: 'center' }}>Loading...</td>
            </tr>
          ) : nodes.length === 0 ? (
            <tr>
              <td colSpan="8" style={{ textAlign: 'center' }}>{t('noNodesFound')}</td>
            </tr>
          ) : (
            nodes.map((node) => (
              <tr key={node.address}>
                <td>{node.name}</td>
                <td>{node.address}</td>
                <td>{node.protocol}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getStatusIcon(node.status)}
                    <span className={`status-${node.status}`}>
                      {node.status === 'online' ? t('status_online') : t('status_offline')}
                    </span>
                  </div>
                </td>
                <td>
                  {node.cpu_usage !== null && node.cpu_usage !== undefined
                    ? `${node.cpu_usage}%`
                    : '-'}
                </td>
                <td>
                  {node.memory_usage !== null && node.memory_usage !== undefined
                    ? `${node.memory_usage}%`
                    : '-'}
                </td>
                <td>
                  {node.response_time !== null && node.response_time !== undefined
                    ? `${(node.response_time * 1000).toFixed(0)}ms`
                    : '-'}
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