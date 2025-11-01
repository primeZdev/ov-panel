import { useState } from 'react';
import apiClient from '../services/api';
import { useTranslation } from 'react-i18next';
import LoadingButton from './LoadingButton';

const AddUserModal = ({ onClose, onUserAdded }) => {
  const [name, setName] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const response = await apiClient.post('/user/create', { name: name, expiry_date: expiryDate });
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
              type="date"
              id="new-user-expiry"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              required
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
