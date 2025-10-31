import { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from '../components/LoadingButton';

const SettingsPage = () => {
  const { t } = useTranslation();
  const [settings, setSettings] = useState({
    tunnel_address: '',
    port: 0,
    protocol: 'tcp',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await apiClient.get('/settings/');
        if (response.data.success && response.data.data) {
          setSettings(response.data.data);
        } else {
          setError(response.data.msg || 'Failed to load settings.');
        }
      } catch (err) {
        setError('An error occurred while fetching settings.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setSettings((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSaving(true);
    setError('');
    setSuccessMessage('');

    const payload = {
      ...settings,
      port: Number(settings.port),
    };

    try {
      const response = await apiClient.put('/settings/update', payload);
      if (response.data.success) {
        setSuccessMessage('Settings updated successfully!');
      } else {
        setError(response.data.msg || 'Failed to update settings.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while saving.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div>Loading settings...</div>;
  }

  return (
    <div id="settings-view" className="view">
      <div className="view-header">
        <h2>{t('settings', 'Panel Settings')}</h2>
      </div>

      <div className="table-container" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <form onSubmit={handleSubmit} style={{ padding: '20px' }}>
          <div className="input-group">
            <label htmlFor="tunnel_address">{t('tunnelAddress', 'Tunnel Address')}</label>
            <input
              type="text"
              id="tunnel_address"
              name="tunnel_address"
              value={settings.tunnel_address || ''}
              onChange={handleChange}
              placeholder="e.g., 10.8.0.0"
            />
          </div>
          <div className="input-group">
            <label htmlFor="port">{t('ovpnPort', 'OVPN Port')}</label>
            <input
              type="number"
              id="port"
              name="port"
              value={settings.port || ''}
              onChange={handleChange}
              required
            />
          </div>
          <div className="input-group">
            <label htmlFor="protocol">{t('th_protocol', 'Protocol')}</label>
            <select
              id="protocol"
              name="protocol"
              value={settings.protocol || 'tcp'}
              onChange={handleChange}
              required
            >
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>

          <div style={{ marginTop: '20px' }}>
            <LoadingButton isLoading={isSaving} type="submit" className="btn" style={{ width: '100%' }}>
              {t('saveSettingsButton', 'Save Settings')}
            </LoadingButton>
          </div>

          {error && <p className="error-message" style={{ marginTop: '15px' }}>{error}</p>}
          {successMessage && <p style={{ color: 'var(--success-color)', marginTop: '15px' }}>{successMessage}</p>}
        </form>
      </div>
    </div>
  );
};

export default SettingsPage;