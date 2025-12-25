import { useEffect, useMemo, useState, useCallback } from 'react';
import { FiUserCheck, FiUsers, FiSearch } from 'react-icons/fi';
import apiClient from '../services/api';
import AddAdminModal from '../components/AddAdminModal';
import EditAdminModal from '../components/EditAdminModal';
import AdminTable from '../components/AdminTable';
import UserStatCard from '../components/UserStatCard';
import Pagination from '../components/Pagination';
import { useTranslation } from 'react-i18next';

const ITEMS_PER_PAGE = 10;

const AdminManagement = () => {
    const [admins, setAdmins] = useState([]);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [selectedAdmin, setSelectedAdmin] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const { t } = useTranslation();

    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    const fetchAdmins = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await apiClient.get('/admin/');
            if (response.data.success) {
                setAdmins(response.data.data || []);
            }
        } catch (error) {
            console.error('Error fetching admins:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAdmins();
    }, [fetchAdmins]);

    const adminStats = useMemo(() => {
        return {
            total: admins.length,
        };
    }, [admins]);

    const filteredAdmins = useMemo(() => {
        return admins.filter(admin =>
            admin.username.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [admins, searchTerm]);

    const totalPages = Math.ceil(filteredAdmins.length / ITEMS_PER_PAGE);

    const paginatedAdmins = useMemo(() => {
        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
        return filteredAdmins.slice(startIndex, startIndex + ITEMS_PER_PAGE);
    }, [filteredAdmins, currentPage]);

    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
        setCurrentPage(1);
    };

    const handleAdminCreated = () => {
        setIsAddModalOpen(false);
        fetchAdmins();
    };

    const handleOpenEditModal = (admin) => {
        setSelectedAdmin(admin);
        setIsEditModalOpen(true);
    };

    const handleAdminUpdated = () => {
        setIsEditModalOpen(false);
        setSelectedAdmin(null);
        fetchAdmins();
    };

    const handleDelete = async (admin) => {
        if (!window.confirm(`${t('deleteAdminConfirm')} ${admin.username}?`)) {
            return;
        }
        try {
            const response = await apiClient.delete(`/admin/${admin.username}`);
            if (response.data.success) {
                alert(t('adminDeletedSuccess'));
                fetchAdmins();
            } else {
                alert(response.data.msg || t('unableToDeleteAdmin'));
            }
        } catch (error) {
            alert(t('errorDeletingAdmin'));
        }
    };

    return (
        <div id="admins-view" className="view">
            <div className="view-header">
                <h2>{t('adminManagement')}</h2>
                <button onClick={() => setIsAddModalOpen(true)} className="btn">
                    {t('addNewAdmin')}
                </button>
            </div>

            <div className="stats-grid" style={{ marginBottom: '30px' }}>
                <UserStatCard
                    icon={<FiUsers className="icon" />}
                    label={t('adminsTotal')}
                    value={adminStats.total}
                    color="var(--accent-color)"
                    className="card-orange"
                />
            </div>

            <div className="search-pagination-controls">
                <div className="search-container">
                    <FiSearch className="search-icon" />
                    <input
                        type="text"
                        placeholder={t('searchByUsername')}
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

            <AdminTable
                admins={paginatedAdmins}
                isLoading={isLoading}
                onEdit={handleOpenEditModal}
                onDelete={handleDelete}
            />

            {isAddModalOpen && (
                <AddAdminModal
                    onClose={() => setIsAddModalOpen(false)}
                    onAdminCreated={handleAdminCreated}
                />
            )}

            {isEditModalOpen && (
                <EditAdminModal
                    admin={selectedAdmin}
                    onClose={() => setIsEditModalOpen(false)}
                    onAdminUpdated={handleAdminUpdated}
                />
            )}
        </div>
    );
};

export default AdminManagement;
