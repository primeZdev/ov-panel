import { useEffect, useMemo, useState, useCallback } from 'react';
import { FiServer, FiCheckCircle, FiXCircle, FiSearch } from 'react-icons/fi';
import apiClient from '../services/api';
import AddNodeModal from '../components/AddNodeModal';
import EditNodeModal from '../components/EditNodeModal';
import NodeTable from '../components/NodeTable';
import UserStatCard from '../components/UserStatCard';
import Pagination from '../components/Pagination'; 
import { useTranslation } from 'react-i18next';

const ITEMS_PER_PAGE = 10;

const NodeManagement = () => {
  const [nodes, setNodes] = useState([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { t } = useTranslation();
  
  
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const fetchNodes = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get('/node/list');
      if (response.data.success) {
        setNodes(response.data.data || []);
      }
    } catch (error) {
      console.error('Error fetching nodes:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNodes();
  }, [fetchNodes]);

  const nodeStats = useMemo(() => {
    const activeCount = nodes.filter((node) => node.status).length;
    return {
      total: nodes.length,
      active: activeCount,
      inactive: nodes.length - activeCount,
    };
  }, [nodes]);

  
  const filteredNodes = useMemo(() => {
    return nodes.filter(node =>
      node.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [nodes, searchTerm]);

  const totalPages = Math.ceil(filteredNodes.length / ITEMS_PER_PAGE);

  const paginatedNodes = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredNodes.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredNodes, currentPage]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1); 
  };


  const handleDelete = async (nodeAddress, nodeName) => {
    if (!window.confirm(`${t('deleteNodeConfirm')} ${nodeName}?`)) {
      return;
    }
    try {
      const response = await apiClient.delete(`/node/delete/${nodeAddress}`);
      if (response.data.success) {
        alert('Node deleted successfully.');
        fetchNodes();
      } else {
        alert(response.data.msg || 'Unable to delete node.');
      }
    } catch (error) {
      alert('Error deleting node.');
    }
  };

  const handleCheckStatus = async (nodeAddress) => {
    try {
        const response = await apiClient.get(`/node/status/${nodeAddress}`);
        alert(response.data.msg || 'Status check complete.');
        fetchNodes();
    } catch (error) {
        alert('Failed to check node status.');
    }
  };

  const handleNodeCreated = () => {
    setIsAddModalOpen(false);
    fetchNodes();
  };
  
  const handleOpenEditModal = (node) => {
    setSelectedNode(node);
    setIsEditModalOpen(true);
  };

  const handleNodeUpdated = () => {
    setIsEditModalOpen(false);
    setSelectedNode(null);
    fetchNodes();
  };

  return (
    <div id="nodes-view" className="view">
      <div className="view-header">
        <h2>{t('nodeManagement')}</h2>
        <button onClick={() => setIsAddModalOpen(true)} className="btn">
          {t('addNewNode')}
        </button>
      </div>

      <div className="stats-grid" style={{ marginBottom: '30px' }}>
        <UserStatCard
          icon={<FiServer className="icon" />}
          label={t('nodesTotal')}
          value={nodeStats.total}
          color="var(--accent-color)"
          className="card-orange"
        />
        <UserStatCard
          icon={<FiCheckCircle className="icon" />}
          label={t('nodesActive')}
          value={nodeStats.active}
          color="var(--success-color)"
          className="card-green"
        />
        <UserStatCard
          icon={<FiXCircle className="icon" />}
          label={t('nodesInactive')}
          value={nodeStats.inactive}
          color="var(--danger-color)"
          className="card-red"
        />
      </div>

      <div className="search-pagination-controls">
        <div className="search-container">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by node name..."
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

      <NodeTable 
        nodes={paginatedNodes} 
        isLoading={isLoading} 
        onDelete={handleDelete}
        onCheckStatus={handleCheckStatus}
        onEdit={handleOpenEditModal}
      />

      {isAddModalOpen && (
        <AddNodeModal
          onClose={() => setIsAddModalOpen(false)}
          onNodeCreated={handleNodeCreated}
        />
      )}
      
      {isEditModalOpen && (
        <EditNodeModal
          node={selectedNode}
          onClose={() => setIsEditModalOpen(false)}
          onNodeUpdated={handleNodeUpdated}
        />
      )}
      
    </div>
  );
};

export default NodeManagement;