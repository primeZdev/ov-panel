import { useState, useEffect, useMemo } from 'react';
import apiClient from '../services/api';
import UserTable from '../components/UserTable';
import AddUserModal from '../components/AddUserModal';
import EditUserModal from '../components/EditUserModal';
import SelectNodeForDownloadModal from '../components/SelectNodeForDownloadModal';
import UserStatCard from '../components/UserStatCard';
import Pagination from '../components/Pagination'; 
import { FiUsers, FiCheckCircle, FiXCircle, FiSearch } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

const ITEMS_PER_PAGE = 10;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const { t } = useTranslation();

  
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get('/user/all');
      if (response.data.success && Array.isArray(response.data.data)) {
        setUsers(response.data.data);
      } else {
        setUsers([]);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      setUsers([]);
    }
  };

  useEffect(() => {
    fetchUsers();
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

  const handleDelete = async (username) => {
    if (!window.confirm(`Are you sure you want to delete user ${username}?`)) return;
    try {
      await apiClient.delete(`/user/delete/${username}`);
      alert('User deleted successfully.');
      fetchUsers();
    } catch (error) {
      alert('Error deleting user.');
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

  return (
    <div id="users-view" className="view">
      <div className="view-header">
        <h2>{t('userManagement')}</h2>
        <button onClick={() => setIsAddModalOpen(true)} className="btn">{t('addNewUser')}</button>
      </div>

      <div className="stats-grid" style={{marginBottom: '30px'}}>
        <UserStatCard 
            icon={<FiUsers className="icon" />} 
            label={t('totalUsers')} 
            value={userStats.total}
            color="var(--accent-color)"
            className="card-orange"
        />
        <UserStatCard 
            icon={<FiCheckCircle className="icon" />} 
            label={t('activeUsers')} 
            value={userStats.active}
            color="var(--success-color)"
            className="card-green"
        />
        <UserStatCard 
            icon={<FiXCircle className="icon" />} 
            label={t('inactiveUsers')} 
            value={userStats.inactive}
            color="var(--danger-color)"
            className="card-red"
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