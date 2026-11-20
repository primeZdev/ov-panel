import { useState } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const AddUserModal = ({ onClose, onUserAdded }) => {
  const [name, setName] = useState('');
  const [expiryInput, setExpiryInput] = useState('');
  const [totalTraffic, setTotalTraffic] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();

  const bytesFromGB = (value) => {
    const cleaned = value?.toString().trim();
    if (!cleaned) return null;
    const parsed = parseFloat(cleaned);
    return Number.isNaN(parsed) ? null : Math.round(parsed * 1024 * 1024 * 1024);
  };

  const parseExpiryInput = (input) => {
    const trimmed = input?.toString().trim();
    if (!trimmed) return null;
    const asNumber = parseInt(trimmed, 10);
    if (!Number.isNaN(asNumber) && trimmed === asNumber.toString()) {
      const date = new Date();
      date.setDate(date.getDate() + asNumber);
      return date.toISOString().split('T')[0];
    }
    return trimmed;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const total = bytesFromGB(totalTraffic);
      const expiryDate = parseExpiryInput(expiryInput);
      if (!expiryDate) {
        setError('Expiry date is required');
        setIsLoading(false);
        return;
      }
      const payload = {
        name: name,
        expiry_date: expiryDate,
        total,
      };
      const response = await apiClient.post('/users/', payload);
      if (response.data.success) {
        alert('User created successfully.');
        onUserAdded();
      } else {
        setError(response.data.msg);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. The username might already exist.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{t('modal_createUserTitle')}</h3>
          <button onClick={onClose} className="close-modal-btn">&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="new-user-name">{t('username')}</label>
            <input
              type="text"
              id="new-user-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required minLength="3" maxLength="10"
            />
          </div>
          <div className="input-group">
            <label htmlFor="new-user-expiry">{t('modal_expiryDate')}</label>
            <input
              type="text"
              id="new-user-expiry"
              value={expiryInput}
              onChange={(e) => setExpiryInput(e.target.value)}
              required
              placeholder={t('modal_expiryPlaceholder')}
            />
            <small className="input-hint">{t('modal_expiryHint')}</small>
          </div>
          <div className="input-group">
            <label htmlFor="new-user-total">{t('modal_totalTraffic')}</label>
            <input
              type="number"
              id="new-user-total"
              value={totalTraffic}
              onChange={(e) => setTotalTraffic(e.target.value)}
              min="0"
              step="0.01"
              placeholder={t('modal_totalTrafficPlaceholder')}
            />
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn btn-secondary">{t('cancelButton')}</button>
            <LoadingButton isLoading={isLoading} type="submit" className="btn">
              {t('createUserButton')}
            </LoadingButton>
          </div>
          {error && <p className="error-message">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default AddUserModal;
