import { useState } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const DownloadFromNodeModal = ({ node, onClose }) => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();

  const handleDownload = async (e) => {
    e.preventDefault();
    if (!username) {
      setError('Please enter a username.');
      return;
    }
    setError('');
    setIsLoading(true);

    try {
      const response = await apiClient.get(`/node/download/ovpn/${node.address}/${username}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // CHANGED: Filename format updated
      link.setAttribute('download', `${username}-${node.name}.ovpn`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      onClose(); // Close modal on success
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to download config for user "${username}".`);
    } finally {
      setIsLoading(false);
    }
  };

  if (!node) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{t('downloadConfigFromNode', 'Download Config from')} "{node.name}"</h3>
          <button onClick={onClose} className="close-modal-btn">&times;</button>
        </div>
        <form onSubmit={handleDownload}>
          <div className="input-group">
            <label htmlFor="username-for-download">{t('th_username', 'Username')}</label>
            <input
              type="text"
              id="username-for-download"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={t('enterUsername', 'Enter username to generate config')}
              required
            />
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">{t('cancelButton')}</button>
            <LoadingButton isLoading={isLoading} type="submit" className="btn btn-success">
              {t('downloadButton', 'Download')}
            </LoadingButton>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default DownloadFromNodeModal;