import { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const SelectNodeForDownloadModal = ({ user, onClose }) => {
  const [nodes, setNodes] = useState([]);
  const [selectedNodeAddress, setSelectedNodeAddress] = useState('');
  const [isLoadingNodes, setIsLoadingNodes] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState('');
  const { t } = useTranslation();

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const response = await apiClient.get('/nodes/');
        if (response.data.success && response.data.data) {
          const available = response.data.data.filter(node => node.status);
          setNodes(available);
          if (available.length > 0) setSelectedNodeAddress(available[0].address);
        }
      } catch (err) {
        setError('Failed to load available nodes.');
      } finally {
        setIsLoadingNodes(false);
      }
    };
    fetchNodes();
  }, []);

  const handleDownload = async (e) => {
    e.preventDefault();
    setError('');
    setIsDownloading(true);

    try {
      let downloadUrl;
      let downloadFileName;

      if (!selectedNodeAddress) throw new Error('No node selected for download.');
      const selectedNode = nodes.find(n => n.address === selectedNodeAddress);
      if (!selectedNode) throw new Error('Selected node not found.');
      downloadUrl = `/nodes/ovpn/${user.uuid}/${selectedNode.id}/`;
      downloadFileName = `${user.name}-${selectedNode.name}.ovpn`;

      const response = await apiClient.get(downloadUrl, { responseType: 'arraybuffer' });
      const contentType = response.headers['content-type'];

      if (contentType && contentType.includes('application/json')) {
        const decoder = new TextDecoder('utf-8');
        const jsonString = decoder.decode(new Uint8Array(response.data));
        const errorData = JSON.parse(jsonString);
        throw new Error(errorData.msg || 'An unknown error occurred on the server.');
      } else {
        const blob = new Blob([response.data], { type: contentType || 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', downloadFileName);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
        onClose();
      }
    } catch (err) {
      setError(err.message || `Failed to download config for user "${user.name}".`);
    } finally {
      setIsDownloading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{t('selectNodeForDownload', 'Select Source for')} {user.name}</h3>
          <button onClick={onClose} className="close-modal-btn">&times;</button>
        </div>
        <form onSubmit={handleDownload}>
          <div className="input-group">
            <label htmlFor="node-select">{t('downloadSource', 'Download Source')}</label>
            {isLoadingNodes ? (
              <p>Loading nodes...</p>
            ) : nodes.length === 0 ? (
              <p>{t('noNodesAvailable', 'No nodes available for download.')}</p>
            ) : (
              <select
                id="node-select"
                value={selectedNodeAddress}
                onChange={(e) => setSelectedNodeAddress(e.target.value)}
                style={{ width: '100%', padding: '10px', backgroundColor: 'var(--background-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                required
              >
                {nodes.map(node => (
                  <option key={node.address} value={node.address}>
                    {node.name} ({node.address})
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">{t('cancelButton')}</button>
            <LoadingButton
              isLoading={isDownloading}
              type="submit"
              className="btn btn-success"
              disabled={isLoadingNodes || nodes.length === 0}
            >
              {t('downloadButton', 'Download')}
            </LoadingButton>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default SelectNodeForDownloadModal;