import { useState, useEffect, useMemo } from 'react';
import apiClient from '../services/api';
import UserTable from '../components/UserTable';
import AddUserModal from '../components/AddUserModal';
import EditUserModal from '../components/EditUserModal';
import SelectNodeForDownloadModal from '../components/SelectNodeForDownloadModal';
import UserStatCard from '../components/UserStatCard';
import Pagination from '../components/Pagination';
import { FiSearch } from 'react-icons/fi';
import { BsPersonFill, BsPersonCheckFill, BsPersonXFill } from 'react-icons/bs';
import { useTranslation } from 'react-i18next';

const ITEMS_PER_PAGE = 10;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [subscriptionSettings, setSubscriptionSettings] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const { t } = useTranslation();


  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get('/users/');
      if (response.data.success && Array.isArray(response.data.data)) {
        setUsers(response.data.data.slice().reverse());
      } else {
        setUsers([]);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      setUsers([]);
    }
  };

  const fetchSubscriptionSettings = async () => {
    try {
      const response = await apiClient.get('/server/settings/');
      if (response.data.success && response.data.data) {
        setSubscriptionSettings(response.data.data);
      }
    } catch (error) {
      console.error("Error fetching subscription settings:", error);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchSubscriptionSettings();
  }, []);

  const userStats = useMemo(() => {
    const activeUsersCount = users.filter(user => user.is_active).length;
    const inactiveUsersCount = users.length - activeUsersCount;
    return {
      total: users.length,
      active: activeUsersCount,
      inactive: inactiveUsersCount,
    };
  }, [users]);

  // Filter and Paginate Data
  const filteredUsers = useMemo(() => {
    return users.filter(user =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [users, searchTerm]);

  const totalPages = Math.ceil(filteredUsers.length / ITEMS_PER_PAGE);

  const paginatedUsers = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredUsers.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredUsers, currentPage]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1);
  };

  const handleDelete = async (uuid, name) => {
    if (!window.confirm(`Are you sure you want to delete user ${name}?`)) return;
    try {
      await apiClient.delete(`/users/${uuid}`);
      alert(`User ${name} deleted successfully.`);
      fetchUsers();
    } catch (error) {
      alert('Error deleting user.');
    }
  };

  const handleToggleStatus = async (user) => {
    const newStatus = !user.is_active;
    const statusLabel = newStatus ? 'activate' : 'deactivate';
    if (!window.confirm(`Are you sure you want to ${statusLabel} user ${user.name}?`)) return;

    try {
      const response = await apiClient.put(`/users/${user.uuid}/status`, {
        name: user.name,
        status: !user.is_active,
        expiry_date: null
      });
      if (response.data.success) {
        alert(`User ${statusLabel}d successfully.`);
        fetchUsers();
      } else {
        alert(`Failed to ${statusLabel} user.`);
      }
    } catch (error) {
      alert(`Error ${statusLabel}ing user.`);
    }
  };

  const handleOpenDownloadModal = (user) => {
    setSelectedUser(user);
    setIsDownloadModalOpen(true);
  };

  const handleUserAdded = () => {
    setIsAddModalOpen(false);
    fetchUsers();
  };

  const handleEdit = (user) => {
    setSelectedUser(user);
    setIsEditModalOpen(true);
  };

  const handleUserUpdated = () => {
    setIsEditModalOpen(false);
    setSelectedUser(null);
    fetchUsers();
  };

  // Generate subscription link for each user
  const getSubscriptionLink = (user) => {
    if (!subscriptionSettings || !user || !user.uuid) return '';
    let prefix = subscriptionSettings.subscription_url_prefix;
    let path = subscriptionSettings.subscription_path || '';
    if (!prefix.endsWith('/')) prefix += '/';
    if (path.startsWith('/')) path = path.slice(1);
    if (path && !path.endsWith('/')) path += '/';
    return `${prefix}${path}${user.uuid}`;
  };

  return (
    <div id="users-view" className="view">
      <div className="view-header">
        <h2>{t('userManagement')}</h2>
        <button onClick={() => setIsAddModalOpen(true)} className="btn">{t('addNewUser')}</button>
      </div>

      <div className="stats-grid" style={{ marginBottom: '30px', display: 'flex', gap: '18px', flexWrap: 'wrap' }}>
        <UserStatCard
          icon={<BsPersonFill style={{ fontSize: 28 }} />}
          label={t('totalUsers')}
          value={userStats.total}
          color="#90caf9"
          className="card-dark"
        />
        <UserStatCard
          icon={<BsPersonCheckFill style={{ fontSize: 28 }} />}
          label={t('activeUsers')}
          value={userStats.active}
          color="#43a047"
          className="card-dark"
        />
        <UserStatCard
          icon={<BsPersonXFill style={{ fontSize: 28 }} />}
          label={t('inactiveUsers')}
          value={userStats.inactive}
          color="#e53935"
          className="card-dark"
        />
      </div>

      <div className="search-pagination-controls">
        <div className="search-container">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by username..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
          />
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      </div>

      <UserTable
        users={paginatedUsers}
        onDelete={handleDelete}
        onDownload={handleOpenDownloadModal}
        onEdit={handleEdit}
        onToggleStatus={handleToggleStatus}
        getSubscriptionLink={getSubscriptionLink}
      />
      {isAddModalOpen && (
        <AddUserModal
          onClose={() => setIsAddModalOpen(false)}
          onUserAdded={handleUserAdded}
        />
      )}
      {isEditModalOpen && (
        <EditUserModal
          user={selectedUser}
          onClose={() => setIsEditModalOpen(false)}
          onUserUpdated={handleUserUpdated}
        />
      )}
      {isDownloadModalOpen && (
        <SelectNodeForDownloadModal
          user={selectedUser}
          onClose={() => setIsDownloadModalOpen(false)}
        />
      )}
    </div>
  );
};

export default UserManagement;