import { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const EditNodeModal = ({ node, onClose, onNodeUpdated }) => {
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
  const [originalAddress, setOriginalAddress] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (node) {
      setFormData({
        name: node.name || '',
        address: node.address || '',
        tunnel_address: node.tunnel_address || '',
        protocol: node.protocol || 'tcp',
        ovpn_port: node.ovpn_port || 1194,
        port: node.port || 0,
        key: node.key || '',
        status: node.status ?? true,
        set_new_setting: true,
      });
      setOriginalAddress(node.address);
    }
  }, [node]);

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
      const response = await apiClient.put(`/node/update/${originalAddress}`, payload);
      if (response.data.success) {
        alert('Node updated successfully.');
        onNodeUpdated();
      } else {
        setError(response.data.msg || 'Unable to update node.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while updating the node.');
    } finally {
      setIsLoading(false);
    }
  };
  
  if (!node) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{t('modal_editNodeTitle', 'Edit Node')}</h3>
          <button onClick={onClose} className="close-modal-btn">&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="edit-name">{t('nodeName')}</label>
            <input type="text" id="edit-name" name="name" value={formData.name} onChange={handleChange} required />
          </div>

          {/* */}
          <div className="input-group">
            <label htmlFor="edit-address">{t('th_address')}</label>
            <input type="text" id="edit-address" name="address" value={formData.address} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="edit-port">{t('nodePort')}</label>
            <input type="number" id="edit-port" name="port" value={formData.port} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="edit-tunnel_address">
              {t('tunnelAddress')}
              <span style={{ color: 'var(--text-secondary)', fontSize: '12px', marginLeft: '8px' }}>
                ({t('optional', 'Optional')})
              </span>
            </label>
            <input type="text" id="edit-tunnel_address" name="tunnel_address" value={formData.tunnel_address} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label htmlFor="edit-protocol">{t('th_protocol')}</label>
            <select id="edit-protocol" name="protocol" value={formData.protocol} onChange={handleChange}>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </div>
          <div className="input-group">
            <label htmlFor="edit-ovpn_port">{t('ovpnPort')}</label>
            <input type="number" id="edit-ovpn_port" name="ovpn_port" value={formData.ovpn_port} onChange={handleChange} required />
          </div>
          <div className="input-group">
            <label htmlFor="edit-key">{t('key')}</label>
            <input type="text" id="edit-key" name="key" value={formData.key} onChange={handleChange} required />
          </div>
          <div className="input-group" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
            <input type="checkbox" id="edit-status" name="status" checked={formData.status} onChange={handleChange} />
            <label htmlFor="edit-status" style={{ marginBottom: 0 }}>{t('status_active')}</label>
          </div>
          
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">{t('cancelButton')}</button>
            <LoadingButton isLoading={isLoading} type="submit" className="btn">
              {t('updateNodeButton', 'Update Node')}
            </LoadingButton>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default EditNodeModal;