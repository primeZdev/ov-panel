import { useState } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const AddNodeModal = ({ onClose, onNodeCreated }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    tunnel_address: '',
    protocol: 'tcp',
    ovpn_port: 1194,
    port: 0,
    key: '',
    status: true,
    set_new_setting: true,
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    const payload = {
      ...formData,
      ovpn_port: Number(formData.ovpn_port),
      port: Number(formData.port),
    };

    try {
      const response = await apiClient.post('/node/add', payload);
      if (response.data.success) {
        alert('Node created successfully.');
        onNodeCreated();
      } else {
        setError(response.data.msg || 'Unable to create node.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while creating the node.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{t('modal_createNodeTitle')}</h3>
          <button onClick={onClose} className="close-modal-btn">&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="name">{t('nodeName')}</label>
            <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} required />
          </div>

          {/* */}
          <div className="input-group">
            <label htmlFor="address">{t('th_address')}</label>
            <input type="text" id="address" name="address" value={formData.address} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="port">{t('nodePort')}</label>
            <input type="number" id="port" name="port" value={formData.port} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="tunnel_address">
              {t('tunnelAddress')}
              <span style={{ color: 'var(--text-secondary)', fontSize: '12px', marginLeft: '8px' }}>
                ({t('optional', 'Optional')})
              </span>
            </label>
            <input type="text" id="tunnel_address" name="tunnel_address" value={formData.tunnel_address} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label htmlFor="protocol">{t('th_protocol')}</label>
            <select id="protocol" name="protocol" value={formData.protocol} onChange={handleChange}>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>
          <div className="input-group">
            <label htmlFor="ovpn_port">{t('ovpnPort')}</label>
            <input type="number" id="ovpn_port" name="ovpn_port" value={formData.ovpn_port} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="key">{t('key')}</label>
            <input type="text" id="key" name="key" value={formData.key} onChange={handleChange} required />
          </div>
          <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
            <input type="checkbox" id="status" name="status" checked={formData.status} onChange={handleChange} />
            <label htmlFor="status" style={{ marginBottom: 0 }}>{t('status_active')}</label>
          </div>
          
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">{t('cancelButton')}</button>
            <LoadingButton isLoading={isLoading} type="submit" className="btn">
              {t('createNodeButton')}
            </LoadingButton>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default AddNodeModal;